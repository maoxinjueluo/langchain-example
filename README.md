# LangChain 智能问答系统（SQLite + Chroma）

基于 FastAPI + Jinja2（SSR）的智能问答系统，包含用户认证、知识库管理、文档解析向量化和多轮问答。

## 技术栈

- Python 3.10
- FastAPI + Jinja2（前后端不分离）
- SQLAlchemy Async + SQLite（`db/app.db`）
- LangChain + Chroma（`db/chroma`）
- bcrypt + JWT

## 核心能力

- 用户注册/登录/邮箱验证/找回密码
- 知识库创建、更新、删除、关键词/分类/标签检索
- TXT/PDF/DOCX 上传，50MB 限制，MD5 去重
- 异步文档解析、分块、向量化入 Chroma
- 问答历史、收藏、反馈、低置信度提示

## 快速启动

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

访问：
- 首页: `http://localhost:8000/`
- 健康检查: `http://localhost:8000/health`

## 测试

```bash
python -m pytest -q
```

## 文档

- API 文档：`docs/API.md`
- 数据库设计：`docs/DB_DESIGN.md`
- 部署文档：`docs/DEPLOYMENT.md`
- 用户手册：`docs/USER_MANUAL.md`
