from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base
from app.db.models import User  # noqa: F401
from app.db.session import engine
from app.api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Auth Service", lifespan=lifespan)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
