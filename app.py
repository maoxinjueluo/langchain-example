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

from common.const import APP_TITLE, APP_HOST, APP_PORT, API_PREFIX, HEALTH_ENDPOINT, MESSAGE_OK
from database import engine, init_db
from routers.user import user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(title=APP_TITLE, lifespan=lifespan)
app.include_router(user_router, prefix=API_PREFIX)


@app.get(HEALTH_ENDPOINT)
async def health() -> Dict[str, str]:
    return {"status": MESSAGE_OK}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
