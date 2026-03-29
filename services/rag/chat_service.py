import math
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import anyio
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.settings import get_settings
from common.const import MessageRole
from models.chat import AnswerFeedback, Conversation, FavoriteQuestion, Message
from services.llm.llm_factory import get_chat_model, get_chroma_store, get_embeddings


def _confidence_from_distance(distance: Optional[float]) -> Optional[float]:
    if distance is None:
        return None
    if math.isnan(distance) or math.isinf(distance):
        return None
    c = 1.0 - float(distance)
    if c < 0:
        c = 0.0
    if c > 1:
        c = 1.0
    return c


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_conversations(self, user_id: uuid.UUID) -> List[Conversation]:
        result = await self._session.execute(
            select(Conversation)
            .where(
                Conversation.user_id == str(user_id),
                Conversation.status == 1
            )
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_conversation(self, user_id: uuid.UUID, conversation_id: uuid.UUID) -> Optional[Conversation]:
        result = await self._session.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == str(user_id),
                Conversation.status == 1
            )
        )
        return result.scalar_one_or_none()

    async def create_conversation(
        self,
        *,
        user_id: uuid.UUID,
        knowledge_base_id: uuid.UUID,
        title: Optional[str],
    ) -> Conversation:
        conv = Conversation(user_id=str(user_id), knowledge_base_id=str(knowledge_base_id), title=title)
        self._session.add(conv)
        await self._session.flush()
        await self._session.refresh(conv)
        return conv

    async def list_messages(self, conversation_id: uuid.UUID, limit: int = 30) -> List[Message]:
        result = await self._session.execute(
            select(Message)
            .where(Message.conversation_id == str(conversation_id), Message.status == 1)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def send_message(
        self,
        *,
        user_id: uuid.UUID,
        knowledge_base_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID],
        message: str,
    ) -> Tuple[uuid.UUID, Message, Message]:
        conv_id: Optional[str] = None
        user_message: Optional[Message] = None
        assistant_message: Optional[Message] = None
        async for event in self.stream_message(
            user_id=user_id,
            knowledge_base_id=str(knowledge_base_id),
            conversation_id=str(conversation_id) if conversation_id else None,
            message=message,
        ):
            if event["type"] == "start":
                conv_id = event["conversation_id"]
                user_message = event["user_message"]
            if event["type"] == "done":
                assistant_message = event["assistant_message"]
        if not conv_id or not user_message or not assistant_message:
            raise ValueError("生成回答失败")
        return conv_id, user_message, assistant_message

    async def stream_message(
        self,
        *,
        user_id: uuid.UUID,
        knowledge_base_id: str,
        conversation_id: Optional[str],
        message: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        msg = message.strip()
        if not msg:
            raise ValueError("问题不能为空")

        conv = None
        if conversation_id:
            conv = await self.get_conversation(user_id, conversation_id)
        if not conv:
            conv = await self.create_conversation(user_id=user_id, knowledge_base_id=knowledge_base_id, title=msg[:28])

        user_message = Message(conversation_id=str(conv.id), role=MessageRole.USER.value, content=msg)
        self._session.add(user_message)
        await self._session.flush()
        await self._session.refresh(user_message)
        yield {"type": "start", "conversation_id": str(conv.id), "user_message": user_message}

        history = await self.list_messages(conv.id, limit=20)
        context, citations, top_distance = await self._retrieve_context(str(knowledge_base_id), msg)
        confidence = _confidence_from_distance(top_distance)

        sys = SystemMessage(
            content=(
                "你是企业知识库问答助手。只能基于提供的资料片段回答。"
                "如果资料不足以回答，请明确说明并给出需要补充的资料类型。"
                "回答要简洁、结构化。"
            )
        )
        prompt = f"资料片段：\n{context}\n\n用户问题：{msg}"
        lc_messages = [sys]
        for h in history[-8:]:
            if h.role == MessageRole.USER.value:
                lc_messages.append(HumanMessage(content=h.content))
        lc_messages.append(HumanMessage(content=prompt))

        model = get_chat_model()
        chunks: List[str] = []
        if hasattr(model, "astream"):
            async for piece in model.astream(lc_messages):
                delta = getattr(piece, "content", piece)
                text = str(delta) if delta is not None else ""
                if not text:
                    continue
                chunks.append(text)
                yield {"type": "delta", "text": text}
        else:
            result = await model.ainvoke(lc_messages)
            text = str(getattr(result, "content", result) or "")
            if text:
                chunks.append(text)
                yield {"type": "delta", "text": text}
        answer_text = "".join(chunks).strip()
        if not answer_text:
            answer_text = "未生成有效答案，请稍后重试。"

        assistant_message = Message(
            conversation_id=str(conv.id),
            role=MessageRole.ASSISTANT.value,
            content=answer_text,
            citations=citations,
            confidence=confidence,
        )
        self._session.add(assistant_message)
        await self._session.flush()
        await self._session.refresh(assistant_message)
        yield {
            "type": "done",
            "conversation_id": str(conv.id),
            "assistant_message": assistant_message,
            "confidence": confidence,
            "citations": citations,
        }

    async def _retrieve_context(
        self, knowledge_base_id: str, query: str, k: Optional[int] = None
    ) -> Tuple[str, List[Dict[str, Any]], Optional[float]]:
        settings = get_settings()
        top_k = k or settings.retrieval_top_k
        try:
            store = get_chroma_store(collection_name=f"kb_{knowledge_base_id}")
            rows = await anyio.to_thread.run_sync(
                store.similarity_search_with_relevance_scores, query, top_k
            )
        except Exception:
            return "", [], None
        if not rows:
            return "", [], None

        context_parts: List[str] = []
        citations: List[Dict[str, Any]] = []
        top_distance: Optional[float] = None
        for doc, score in rows:
            dist = 1.0 - float(score)
            if top_distance is None:
                top_distance = float(dist)
            meta = doc.metadata or {}
            title = str(meta.get("title") or "")
            snippet = str(meta.get("snippet") or doc.page_content[:360])
            context_parts.append(f"[来源: {title}]\n{doc.page_content}\n")
            citations.append(
                {
                    "chunkId": str(meta.get("chunk_id") or ""),
                    "documentId": str(meta.get("document_id") or ""),
                    "title": title,
                    "snippet": snippet,
                }
            )
        return "\n".join(context_parts), citations, top_distance

    async def add_favorite(self, *, user_id: uuid.UUID, message_id: str) -> FavoriteQuestion:
        exists = (
            await self._session.execute(
                select(FavoriteQuestion).where(
                    FavoriteQuestion.user_id == str(user_id),
                    FavoriteQuestion.message_id == message_id,
                    FavoriteQuestion.status == 1,
                )
            )
        ).scalar_one_or_none()
        if exists:
            return exists
        row = FavoriteQuestion(user_id=str(user_id), message_id=message_id)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def add_feedback(self, *, message_id: str, is_helpful: bool, reason: Optional[str]) -> AnswerFeedback:
        row = AnswerFeedback(message_id=message_id, is_helpful=is_helpful, reason=reason)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row


def _cosine_distance(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 1.0
    n = min(len(a), len(b))
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(n):
        x = float(a[i])
        y = float(b[i])
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 1.0
    cos = dot / (math.sqrt(na) * math.sqrt(nb))
    return 1.0 - cos
