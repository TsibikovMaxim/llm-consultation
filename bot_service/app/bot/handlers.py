from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()

TOKEN_KEY_PREFIX = "token:"

HELP_TEXT = (
    "Доступные команды:\n"
    "/token <jwt> — сохранить JWT-токен\n"
    "/help — показать это сообщение\n\n"
    "Чтобы получить токен, зарегистрируйтесь и войдите через Swagger Auth Service: "
    "http://localhost:8000/docs"
)


@router.message(Command("start", "help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT)


@router.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /token <ваш_jwt>")
        return

    token = parts[1].strip()
    try:
        decode_and_validate(token)
    except ValueError as e:
        await message.answer(f"Недействительный токен: {e}")
        return

    redis = get_redis()
    key = f"{TOKEN_KEY_PREFIX}{message.from_user.id}"
    await redis.set(key, token)
    await message.answer("Токен принят и сохранён.")


@router.message(F.text)
async def handle_message(message: Message):
    redis = get_redis()
    key = f"{TOKEN_KEY_PREFIX}{message.from_user.id}"
    token = await redis.get(key)

    if not token:
        await message.answer(
            "Вы не авторизованы. Получите JWT-токен через Auth Service "
            "и отправьте его командой /token <jwt>\n\nНапишите /help для справки."
        )
        return

    try:
        decode_and_validate(token)
    except ValueError:
        await redis.delete(key)
        await message.answer(
            "Токен недействителен или истёк. Получите новый JWT через Auth Service "
            "и отправьте командой /token <jwt>"
        )
        return

    loading_msg = await message.answer(
        "Генерирую ответ...\n"
        "[          ] 0%"
    )
    llm_request.delay(message.chat.id, message.text, loading_msg.message_id)
