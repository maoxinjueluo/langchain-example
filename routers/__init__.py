from routers.pages import router as pages_router
from routers.auth_pages import router as auth_pages_router
from routers.kb_pages import router as kb_pages_router
from routers.chat_pages import router as chat_pages_router

__all__ = ["auth_pages_router", "chat_pages_router", "kb_pages_router", "pages_router"]
