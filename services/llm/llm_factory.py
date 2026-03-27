from typing import List

from common.settings import get_settings


class _LocalEmbeddings:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._vec(text)

    def _vec(self, text: str) -> List[float]:
        base = float((sum(ord(c) for c in text) % 97) + 1) / 100.0
        return [base] * 1536


class _LocalChatModel:
    async def ainvoke(self, messages):
        class R:
            def __init__(self, content: str):
                self.content = content

        last = messages[-1].content if messages else ""
        return R("未配置 OPENAI_API_KEY，当前为本地模拟回答。\n\n" + last[:600])

    async def astream(self, messages):
        result = await self.ainvoke(messages)
        text = getattr(result, "content", "")
        step = 12
        for i in range(0, len(text), step):
            yield text[i : i + step]


def get_embeddings():
    settings = get_settings()
    if not settings.openai_api_key:
        return _LocalEmbeddings()

    from langchain_community.embeddings import DashScopeEmbeddings

    return DashScopeEmbeddings(dashscope_api_key=settings.openai_api_key)


def get_chat_model():
    settings = get_settings()
    if not settings.openai_api_key:
        return _LocalChatModel()

    from langchain_community.chat_models import ChatTongyi

    return ChatTongyi(model=settings.openai_chat_model, api_key=settings.openai_api_key, temperature=0.2)


def get_chroma_store(*, collection_name: str):
    settings = get_settings()
    from pathlib import Path

    from langchain_chroma import Chroma

    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_dir,
    )
