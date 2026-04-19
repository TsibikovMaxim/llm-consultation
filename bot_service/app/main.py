import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bot.dispatcher import create_bot_and_dispatcher
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot, dp = create_bot_and_dispatcher(settings.TELEGRAM_BOT_TOKEN)
    task = asyncio.create_task(dp.start_polling(bot))
    yield
    task.cancel()
    await bot.session.close()


app = FastAPI(title="Bot Service", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}
