# 部署文档

## 本地部署

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Docker Compose

```bash
docker compose up --build
```

默认挂载：
- `./db/app.db`
- `./db/uploads`
- `./db/chroma`

## 环境变量

- `ENV`：`dev/test/prod`
- `APP_BASE_URL`
- `DATABASE_URL`（推荐 SQLite: `sqlite+aiosqlite:///db/app.db`）
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRES_MINUTES`
- `REMEMBER_ME_DAYS`
- `MAX_UPLOAD_MB`
- `UPLOAD_DIR`
- `CHROMA_DIR`
- `RETRIEVAL_TOP_K`
- `CONFIDENCE_THRESHOLD`
- `OPENAI_API_KEY`（可选）

## 安全建议

- 生产环境强制 HTTPS
- `SECRET_KEY` 使用高强度随机值
- 开启反向代理限流（Nginx/Traefik）
- 上传目录与应用目录权限隔离
- 定期清理过期 token/session

