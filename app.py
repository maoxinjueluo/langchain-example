"""
Author: hyx yuxin.huang@tenclass.com
Date: 2026-03-22 16:14:42
LastEditors: hyx yuxin.huang@tenclass.com
LastEditTime: 2026-03-23 15:56:48
FilePath: /langchain-example/app.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from common.const import APP_TITLE, APP_HOST, APP_PORT, HEALTH_ENDPOINT, MESSAGE_OK
from database import engine, init_db
from routers import auth_pages_router, chat_pages_router, kb_pages_router, pages_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(title=APP_TITLE, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_pages_router)
app.include_router(chat_pages_router)
app.include_router(kb_pages_router)
app.include_router(pages_router)


@app.get(HEALTH_ENDPOINT)
async def health() -> Dict[str, str]:
    return {"status": MESSAGE_OK}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
