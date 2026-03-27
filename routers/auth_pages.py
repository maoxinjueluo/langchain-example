from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from common.security import create_access_token
from common.settings import get_settings
from database import get_session
from routers.deps import get_current_user_optional
from services.auth.auth_service import AuthService


templates = Jinja2Templates(directory="templates")

router = APIRouter()


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


def _set_cookie(resp: RedirectResponse, token: str, remember_me: bool) -> None:
    settings = get_settings()
    max_age = settings.remember_me_days * 24 * 3600 if remember_me else settings.access_token_expires_minutes * 60
    secure = settings.env not in {"dev", "test"}
    resp.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user=Depends(get_current_user_optional)) -> HTMLResponse:
    if user:
        return _redirect("/")
    return templates.TemplateResponse(request, "auth/login.html", {"error": None})


@router.post("/login")
async def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember_me: str = Form(default=""),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    user = await service.verify_credentials(email=email, password=password)
    if not user:
        return templates.TemplateResponse(request, "auth/login.html", {"error": "邮箱或密码错误"}, status_code=400)
    if not user.is_email_verified:
        return templates.TemplateResponse(request, "auth/login.html", {"error": "请先完成邮箱验证"}, status_code=400)
    await service.create_session(user=user, remember_me=bool(remember_me), user_agent=request.headers.get("user-agent"))
    token = create_access_token(user_id=str(user.id), role=user.role, remember_me=bool(remember_me))
    resp = _redirect("/")
    _set_cookie(resp, token, bool(remember_me))
    return resp


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user=Depends(get_current_user_optional)) -> HTMLResponse:
    if user:
        return _redirect("/")
    return templates.TemplateResponse(request, "auth/register.html", {"error": None})


@router.post("/register")
async def register_action(
    request: Request,
    email: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    try:
        user = await service.create_user(email=email, name=name, password=password)
    except ValueError as e:
        return templates.TemplateResponse(request, "auth/register.html", {"error": str(e)}, status_code=400)
    await service.send_verification_email(user)
    return templates.TemplateResponse(
        request,
        "auth/register_done.html",
        {"email": user.email},
    )


@router.get("/verify")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    ok = await service.verify_email(token)
    return _redirect("/login?verified=1" if ok else "/login?verified=0")


@router.get("/forgot", response_class=HTMLResponse)
async def forgot_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "auth/forgot.html", {"sent": False})


@router.post("/forgot", response_class=HTMLResponse)
async def forgot_action(request: Request, email: str = Form(...), session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    await service.send_password_reset_email(email)
    return templates.TemplateResponse(request, "auth/forgot.html", {"sent": True})


@router.get("/reset", response_class=HTMLResponse)
async def reset_page(request: Request, token: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "auth/reset.html", {"token": token, "error": None})


@router.post("/reset", response_class=HTMLResponse)
async def reset_action(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    try:
        ok = await service.reset_password(raw_token=token, new_password=password)
    except ValueError as e:
        return templates.TemplateResponse(request, "auth/reset.html", {"token": token, "error": str(e)}, status_code=400)
    if not ok:
        return templates.TemplateResponse(request, "auth/reset.html", {"token": token, "error": "链接无效或已过期"}, status_code=400)
    return _redirect("/login?reset=1")


@router.post("/logout")
async def logout_action() -> RedirectResponse:
    resp = _redirect("/login")
    resp.delete_cookie("access_token", path="/")
    return resp
