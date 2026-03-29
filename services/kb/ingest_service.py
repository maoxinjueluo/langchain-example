import traceback
from pathlib import Path
from typing import List, Optional

import anyio
# from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pypdf import PdfReader
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.files import calc_md5, ensure_upload_allowed
from common.settings import get_settings
from common.const import KBDocumentStatus, UserRole
from models.chunk import DocChunk
from models.kb import KBDocument, KBTag, KnowledgeBase, KnowledgeBaseTag
from services.llm.llm_factory import get_chroma_store, get_embeddings
from loguru import logger


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    r = PdfReader(str(path))
    parts: List[str] = []
    for page in r.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _read_docx(path: Path) -> str:
    # 暂时注释掉，因为DocxDocument未导入
    # d = DocxDocument(str(path))
    # parts: List[str] = []
    # for p in d.paragraphs:
    #     if p.text:
    #         parts.append(p.text)
    # return "\n".join(parts)
    raise NotImplementedError("DocxDocument not imported")


def _load_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".txt":
        return _read_txt(path)
    if ext == ".pdf":
        return _read_pdf(path)
    if ext == ".docx":
        return _read_docx(path)
    raise ValueError("不支持的文件格式")


class KBIngestService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_kb(
        self,
        *,
        owner_user_id,
        name: str,
        description: Optional[str],
        visibility: str,
        category: Optional[str] = None,
        permission_level: str = UserRole.ADMIN.value,
    ) -> KnowledgeBase:
        kb = KnowledgeBase(
            owner_user_id=str(owner_user_id),
            name=name.strip(),
            description=description.strip() if description else None,
            visibility=visibility,
            category=category.strip() if category else None,
            permission_level=permission_level,
        )
        self._session.add(kb)
        await self._session.flush()
        await self._session.refresh(kb)
        return kb

    async def update_kb(
        self, kb_id, *, name: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None
    ) -> Optional[KnowledgeBase]:
        kb = await self.get_kb(kb_id)
        if not kb:
            return None
        if name is not None:
            kb.name = name.strip()
        if description is not None:
            kb.description = description.strip() if description else None
        if category is not None:
            kb.category = category.strip() if category else None
        kb.version += 1
        await self._session.flush()
        return kb

    async def delete_kb(self, kb_id) -> bool:
        kb = await self.get_kb(kb_id)
        if not kb:
            return False
        docs = await self.list_documents(kb_id)
        for d in docs:
            await self.delete_document(d.id)
        await self._session.execute(update(KnowledgeBaseTag).where(KnowledgeBaseTag.knowledge_base_id == str(kb_id)).values(status=0))
        kb.status = 0
        await self._session.flush()
        return True

    async def list_kbs(self) -> List[KnowledgeBase]:
        result = await self._session.execute(
            select(KnowledgeBase).where(KnowledgeBase.status == 1).order_by(KnowledgeBase.updated_at.desc())
        )
        return list(result.scalars().all())

    async def search_kbs(
        self,
        *,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[KnowledgeBase]:
        stmt = select(KnowledgeBase).where(KnowledgeBase.status == 1)
        if keyword:
            key = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(KnowledgeBase.name.like(key), KnowledgeBase.description.like(key)))
        if category:
            stmt = stmt.where(KnowledgeBase.category == category)
        if tag:
            tag_row = (
                await self._session.execute(select(KBTag).where(KBTag.name == tag, KBTag.status == 1))
            ).scalar_one_or_none()
            if not tag_row:
                return []
            links = await self._session.execute(
                select(KnowledgeBaseTag.knowledge_base_id).where(KnowledgeBaseTag.tag_id == str(tag_row.id))
            )
            kb_ids = [row[0] for row in links.all()]
            if not kb_ids:
                return []
            stmt = stmt.where(KnowledgeBase.id.in_(kb_ids))
        result = await self._session.execute(stmt.order_by(KnowledgeBase.updated_at.desc()))
        return list(result.scalars().all())

    async def get_kb(self, kb_id) -> Optional[KnowledgeBase]:
        result = await self._session.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
        return result.scalar_one_or_none()

    async def list_documents(self, kb_id) -> List[KBDocument]:
        result = await self._session.execute(
            select(KBDocument)
            .where(KBDocument.knowledge_base_id == str(kb_id), KBDocument.status == 1)
            .order_by(KBDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_tag(self, kb_id, tag_name: str) -> None:
        name = tag_name.strip()
        if not name:
            return
        tag = (await self._session.execute(select(KBTag).where(KBTag.name == name))).scalar_one_or_none()
        if not tag:
            tag = KBTag(name=name)
            self._session.add(tag)
            await self._session.flush()
        exists = (
            await self._session.execute(
                select(KnowledgeBaseTag).where(
                    KnowledgeBaseTag.knowledge_base_id == str(kb_id),
                    KnowledgeBaseTag.tag_id == str(tag.id),
                    KnowledgeBaseTag.status == 1,
                )
            )
        ).scalar_one_or_none()
        if not exists:
            self._session.add(KnowledgeBaseTag(knowledge_base_id=str(kb_id), tag_id=str(tag.id)))
            await self._session.flush()

    async def ingest_upload(self, *, kb_id, upload) -> KBDocument:
        ensure_upload_allowed(upload)
        settings = get_settings()
        size = getattr(upload, "size", None)
        if size is None:
            data = await upload.read()
            size = len(data)
            await upload.seek(0)
        if size > settings.max_upload_mb * 1024 * 1024:
            raise ValueError("文件过大")

        md5 = await calc_md5(upload)
        exists = await self._session.execute(
            select(KBDocument).where(KBDocument.knowledge_base_id == kb_id, KBDocument.md5 == md5)
        )
        if exists.scalar_one_or_none():
            raise ValueError("文件已存在（MD5 去重）")

        filename = upload.filename or "file"
        ext = Path(filename).suffix.lower()
        kb_dir = Path(settings.upload_dir) / "kb" / str(kb_id)
        await anyio.to_thread.run_sync(lambda: kb_dir.mkdir(parents=True, exist_ok=True))
        storage_path = kb_dir / f"{md5}_{filename}"

        await upload.seek(0)
        data = await upload.read()
        await anyio.to_thread.run_sync(storage_path.write_bytes, data)
        await upload.seek(0)

        doc = KBDocument(
            knowledge_base_id=kb_id,
            title=filename,
            storage_path=str(storage_path),
            md5=md5,
            size_bytes=size,
            processing_status=KBDocumentStatus.UPLOADED.value,
            file_ext=ext,
            mime_type=upload.content_type,
        )
        self._session.add(doc)
        await self._session.flush()
        await self._session.refresh(doc)

        await self._process_document(doc)
        await self._session.refresh(doc)
        return doc

    async def _process_document(self, doc: KBDocument) -> None:
        await self._session.execute(
            update(KBDocument)
            .where(KBDocument.id == doc.id)
            .values(
                processing_status=KBDocumentStatus.CHUNKING.value,
                error_message=None
            )
        )
        await self._session.flush()

        try:
            text = await anyio.to_thread.run_sync(_load_text, Path(doc.storage_path))
            splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=140)
            chunks = splitter.split_text(text)
            if not chunks:
                raise ValueError("文档解析后无可用内容")

            await self._session.execute(
                update(KBDocument)
                .where(KBDocument.id == doc.id)
                .values(processing_status=KBDocumentStatus.EMBEDDING.value)
            )
            await self._session.flush()

            rows: List[DocChunk] = []
            lc_docs: List[Document] = []
            for i, content in enumerate(chunks):
                chunk_id = str(doc.id) + ":" + str(i)
                rows.append(
                    DocChunk(
                        knowledge_base_id=str(doc.knowledge_base_id),
                        document_id=str(doc.id),
                        chunk_index=i,
                        content=content,
                        embedding=None,
                        chunk_metadata={"title": doc.title, "storage_path": doc.storage_path, "md5": doc.md5},
                    )
                )
                lc_docs.append(
                    Document(
                        page_content=content,
                        id=chunk_id,
                        metadata={
                            "chunk_id": chunk_id,
                            "document_id": str(doc.id),
                            "knowledge_base_id": str(doc.knowledge_base_id),
                            "title": doc.title,
                            "snippet": content[:360],
                        },
                    )
                )
            self._session.add_all(rows)
            await self._session.flush()
            store = get_chroma_store(collection_name=f"kb_{doc.knowledge_base_id}")
            await anyio.to_thread.run_sync(store.add_documents, lc_docs)
            await self._session.execute(
                update(KBDocument)
                .where(KBDocument.id == doc.id)
                .values(processing_status=KBDocumentStatus.READY.value)
            )
            await self._session.flush()
        except Exception as e:
            logger.error(f'处理失败，详细原因：{traceback.format_exc()}')
            await self._session.execute(
                update(KBDocument)
                .where(KBDocument.id == doc.id)
                .values(processing_status=KBDocumentStatus.FAILED.value, error_message=str(e)[:2000])
            )
            await self._session.flush()

    async def delete_document(self, document_id) -> bool:
        doc = (await self._session.execute(select(KBDocument).where(KBDocument.id == document_id))).scalar_one_or_none()
        if not doc:
            return False
        chunks = (
            await self._session.execute(select(DocChunk).where(DocChunk.document_id == str(document_id)))
        ).scalars().all()
        if chunks:
            store = get_chroma_store(collection_name=f"kb_{doc.knowledge_base_id}")
            ids = [f"{doc.id}:{c.chunk_index}" for c in chunks]
            await anyio.to_thread.run_sync(store.delete, ids)
            for c in chunks:
                c.status = 0
        doc.status = 0
        await self._session.flush()
        return True


if __name__ == '__main__':
    import os
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file = os.path.join(
        base_path, 'db', 'uploads', 'kb', 'faee97e0-92e0-4278-84fc-452195c3e9d6',
        '64d8552ee31435ea612f981110f6bdfb_滕王阁序.docx'
    )
    print(_read_docx(file))
