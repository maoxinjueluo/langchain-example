from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.security import decode_access_token
from database import async_session_maker, get_session
from common.settings import get_settings
from models.chat import Message
from models.auth import User
from models.kb import KnowledgeBase
from routers.deps import require_user
from services.rag.chat_service import ChatService


templates = Jinja2Templates(directory="templates")

router = APIRouter()


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(
    request: Request,
    c: Optional[str] = None,
    kb: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_user),
):
    chat = ChatService(session)
    conversations = await chat.list_conversations(user.id)

    kbs = (
        await session.execute(
            select(KnowledgeBase).where(
                (KnowledgeBase.visibility == "org") | (KnowledgeBase.owner_user_id == str(user.id))
            )
        )
    ).scalars().all()
    kb_list = list(kbs)

    active_conv = None
    active_messages = []
    active_kb_id = kb or (conversations[0].knowledge_base_id if conversations else (kb_list[0].id if kb_list else None))
    if c:
        active_conv = await chat.get_conversation(user.id, c)
    if active_conv:
        active_messages = await chat.list_messages(active_conv.id, limit=60)
        active_kb_id = active_conv.knowledge_base_id

    return templates.TemplateResponse(
        request,
        "chat/index.html",
        {
            "user": user,
            "kbs": kb_list,
            "confidence_threshold": get_settings().confidence_threshold,
            "active_kb_id": active_kb_id,
            "conversations": conversations,
            "active_conversation": active_conv,
            "messages": active_messages,
            "error": None,
        },
    )


@router.post("/chat/send")
async def chat_send(
    request: Request,
    message: str = Form(...),
    knowledge_base_id: str = Form(...),
    conversation_id: Optional[str] = Form(default=None),
    session: AsyncSession = Depends(get_session),
    user=Depends(require_user),
):
    chat = ChatService(session)
    try:
        conv_id, _, _ = await chat.send_message(
            user_id=user.id,
            knowledge_base_id=knowledge_base_id,
            conversation_id=conversation_id,
            message=message,
        )
    except Exception as e:
        return templates.TemplateResponse(
            request,
            "chat/error.html",
            {"error": str(e)},
            status_code=400,
        )
    return _redirect(f"/chat?c={conv_id}")


@router.post("/chat/favorite")
async def chat_favorite(
    message_id: str = Form(...),
    session: AsyncSession = Depends(get_session),
    user=Depends(require_user),
):
    chat = ChatService(session)
    await chat.add_favorite(user_id=user.id, message_id=message_id)
    return _redirect("/chat")


@router.post("/chat/feedback")
async def chat_feedback(
    message_id: str = Form(...),
    is_helpful: str = Form(...),
    reason: str = Form(default=""),
    session: AsyncSession = Depends(get_session),
    user=Depends(require_user),
):
    chat = ChatService(session)
    await chat.add_feedback(message_id=message_id, is_helpful=is_helpful == "1", reason=reason or None)
    return _redirect("/chat")


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket):
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        payload = decode_access_token(token)
        user_id = str(payload.get("sub") or "")
    except Exception:
        await websocket.close(code=4401)
        return
    if not user_id:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    async with async_session_maker() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            await websocket.close(code=4401)
            return
        chat = ChatService(session)
        while True:
            try:
                data = await websocket.receive_json()
                message = str(data.get("message") or "").strip()
                kb_id = str(data.get("knowledge_base_id") or "")
                conv_id = data.get("conversation_id")
                if not message or not kb_id:
                    await websocket.send_json({"type": "error", "message": "参数错误"})
                    continue
                async for event in chat.stream_message(
                    user_id=user.id,
                    knowledge_base_id=kb_id,
                    conversation_id=str(conv_id) if conv_id else None,
                    message=message,
                ):
                    if event["type"] == "start":
                        await websocket.send_json(
                            {"type": "start", "conversation_id": event["conversation_id"]}
                        )
                    elif event["type"] == "delta":
                        await websocket.send_json({"type": "delta", "text": event["text"]})
                    elif event["type"] == "done":
                        await websocket.send_json(
                            {
                                "type": "done",
                                "conversation_id": event["conversation_id"],
                                "message_id": str(event["assistant_message"].id),
                                "confidence": event["confidence"],
                                "citations": event["citations"],
                            }
                        )
                        break
                await session.commit()
            except Exception as e:
                await session.rollback()
                await websocket.send_json({"type": "error", "message": str(e)})
