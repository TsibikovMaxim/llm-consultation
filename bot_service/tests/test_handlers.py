from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.bot.handlers import TOKEN_KEY_PREFIX
from app.core.config import settings


def make_token(expire_delta: timedelta = timedelta(hours=1)) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": "42", "role": "user", "iat": now, "exp": now + expire_delta},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )


def make_message(text: str, user_id: int = 123, chat_id: int = 123) -> AsyncMock:
    message = AsyncMock()
    message.text = text
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.chat = MagicMock()
    message.chat.id = chat_id
    return message


@pytest.mark.asyncio
async def test_cmd_token_saves_to_redis(fake_redis):
    token = make_token()
    message = make_message(f"/token {token}")

    with patch("app.bot.handlers.get_redis", return_value=fake_redis):
        from app.bot.handlers import cmd_token
        await cmd_token(message)

    stored = await fake_redis.get(f"{TOKEN_KEY_PREFIX}123")
    assert stored == token
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_no_token(fake_redis):
    message = make_message("Привет, бот!")

    with patch("app.bot.handlers.get_redis", return_value=fake_redis), \
         patch("app.bot.handlers.llm_request") as mock_task:
        from app.bot.handlers import handle_message
        await handle_message(message)

    mock_task.delay.assert_not_called()
    message.answer.assert_called_once()
    assert "авторизован" in message.answer.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_message_with_valid_token(fake_redis):
    token = make_token()
    await fake_redis.set(f"{TOKEN_KEY_PREFIX}123", token)
    message = make_message("Что такое Python?")

    with patch("app.bot.handlers.get_redis", return_value=fake_redis), \
         patch("app.bot.handlers.llm_request") as mock_task:
        from app.bot.handlers import handle_message
        await handle_message(message)

    args = mock_task.delay.call_args[0]
    assert args[0] == 123
    assert args[1] == "Что такое Python?"
