from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from routers.deps import require_admin
from services.kb.ingest_service import KBIngestService


templates = Jinja2Templates(directory="templates")

router = APIRouter()


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


@router.get("/kb", response_class=HTMLResponse)
async def kb_index(
    request: Request,
    keyword: str = Query(default=""),
    category: str = Query(default=""),
    tag: str = Query(default=""),
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    service = KBIngestService(session)
    if keyword or category or tag:
        kbs = await service.search_kbs(keyword=keyword or None, category=category or None, tag=tag or None)
    else:
        kbs = await service.list_kbs()
    return templates.TemplateResponse(
        request, "kb/index.html", {"kbs": kbs, "user": user, "error": None, "keyword": keyword, "category": category, "tag": tag}
    )


@router.post("/kb")
async def kb_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
    visibility: str = Form(default="private"),
    category: str = Form(default=""),
    tags: str = Form(default=""),
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    service = KBIngestService(session)
    kb = await service.create_kb(
        owner_user_id=user.id,
        name=name,
        description=description or None,
        visibility=visibility,
        category=category or None,
    )
    if tags.strip():
        for t in tags.split(","):
            await service.add_tag(kb.id, t)
    return _redirect(f"/kb/{kb.id}")


@router.post("/kb/{kb_id}/update")
async def kb_update(
    kb_id: str,
    name: str = Form(default=""),
    description: str = Form(default=""),
    category: str = Form(default=""),
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    service = KBIngestService(session)
    await service.update_kb(kb_id, name=name or None, description=description, category=category)
    return _redirect(f"/kb/{kb_id}")


@router.post("/kb/{kb_id}/delete")
async def kb_delete(kb_id: str, session: AsyncSession = Depends(get_session), user=Depends(require_admin)):
    service = KBIngestService(session)
    await service.delete_kb(kb_id)
    return _redirect("/kb")


@router.post("/kb/{kb_id}/documents/{document_id}/delete")
async def kb_document_delete(
    kb_id: str,
    document_id: str,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    service = KBIngestService(session)
    await service.delete_document(document_id)
    return _redirect(f"/kb/{kb_id}")


@router.get("/kb/{kb_id}", response_class=HTMLResponse)
async def kb_detail(kb_id: str, request: Request, session: AsyncSession = Depends(get_session), user=Depends(require_admin)):
    service = KBIngestService(session)
    kb = await service.get_kb(kb_id)
    if not kb:
        return _redirect("/kb")
    docs = await service.list_documents(kb_id)
    return templates.TemplateResponse(
        request,
        "kb/detail.html",
        {"kb": kb, "docs": docs, "user": user, "error": None},
    )


@router.post("/kb/{kb_id}/upload")
async def kb_upload(
    kb_id: str,
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    service = KBIngestService(session)
    kb = await service.get_kb(kb_id)
    if not kb:
        return _redirect("/kb")
    try:
        await service.ingest_upload(kb_id=kb_id, upload=file)
    except Exception as e:
        docs = await service.list_documents(kb_id)
        return templates.TemplateResponse(
            request,
            "kb/detail.html",
            {"kb": kb, "docs": docs, "user": user, "error": str(e)},
            status_code=400,
        )
    return _redirect(f"/kb/{kb_id}")
