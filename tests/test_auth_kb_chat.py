import re

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient


class FakeEmbeddings:
    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text_):
        return self._vec(text_)

    def _vec(self, text_):
        base = float((sum(ord(c) for c in text_) % 97) + 1) / 100.0
        return [base] * 1536


class FakeChatModel:
    async def ainvoke(self, messages):
        class R:
            def __init__(self, content):
                self.content = content

        last = messages[-1].content
        return R("测试回答：" + last[:40])


@pytest.mark.asyncio
async def test_auth_kb_ingest_chat(monkeypatch: pytest.MonkeyPatch):
    from app import app
    from database import engine, init_db
    from models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await init_db()

    captured = {"content": ""}

    def _send_email(*, to: str, subject: str, content: str) -> None:
        captured["content"] = content

    monkeypatch.setattr("services.auth.auth_service.send_email", _send_email)
    monkeypatch.setattr("services.kb.ingest_service.get_embeddings", lambda: FakeEmbeddings())
    monkeypatch.setattr("services.rag.chat_service.get_embeddings", lambda: FakeEmbeddings())
    monkeypatch.setattr("services.rag.chat_service.get_chat_model", lambda: FakeChatModel())

    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/register")
            assert r.status_code == 200

            r = await client.post(
                "/register",
                data={"email": "admin@example.com", "name": "Admin", "password": "Passw0rd1"},
            )
            assert r.status_code == 200

            m = re.search(r"token=([A-Za-z0-9_\-\.]+)", captured["content"])
            assert m
            token = m.group(1)

            r = await client.get(f"/verify?token={token}")
            assert r.status_code in (302, 303)

            r = await client.post(
                "/login",
                data={"email": "admin@example.com", "password": "Passw0rd1", "remember_me": "1"},
                follow_redirects=False,
            )
            assert r.status_code == 303
            assert "access_token=" in r.headers.get("set-cookie", "")

            client.cookies.update(r.cookies)
            r = await client.get("/")
            assert r.status_code == 200

            r = await client.post(
                "/kb",
                data={"name": "DemoKB", "description": "desc", "visibility": "org"},
                follow_redirects=False,
            )
            assert r.status_code == 303
            kb_url = r.headers["location"]

            r = await client.get(kb_url)
            assert r.status_code == 200

            r = await client.post(
                kb_url + "/upload",
                files={"file": ("demo.txt", b"hello world\nthis is a test", "text/plain")},
                follow_redirects=False,
            )
            assert r.status_code == 303

            r = await client.get("/chat")
            assert r.status_code == 200

            kb_id = kb_url.rsplit("/", 1)[-1]
            r = await client.post(
                "/chat/send",
                data={"knowledge_base_id": kb_id, "message": "hello?"},
                follow_redirects=False,
            )
            assert r.status_code == 303
            conv_url = r.headers["location"]

            r = await client.get(conv_url)
            assert r.status_code == 200
            assert "测试回答" in r.text

            from models.chat import Message
            from sqlalchemy import select
            from database import async_session_maker

            async with async_session_maker() as s:
                msg = (
                    await s.execute(
                        select(Message).where(Message.role == "assistant").order_by(Message.created_at.desc())
                    )
                ).scalar_one()

            r = await client.post("/chat/favorite", data={"message_id": str(msg.id)}, follow_redirects=False)
            assert r.status_code == 303

            r = await client.post(
                "/chat/feedback",
                data={"message_id": str(msg.id), "is_helpful": "1", "reason": "ok"},
                follow_redirects=False,
            )
            assert r.status_code == 303

            r = await client.get("/kb?keyword=DemoKB")
            assert r.status_code == 200
