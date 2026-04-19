import httpx
import pytest
import respx

from app.core.config import settings
from app.services.openrouter_client import call_openrouter


@pytest.mark.asyncio
@respx.mock
async def test_call_openrouter_success():
    mock_response = {
        "choices": [{"message": {"content": "Python is a programming language."}}]
    }

    respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = await call_openrouter("What is Python?")
    assert result == "Python is a programming language."


@pytest.mark.asyncio
@respx.mock
async def test_call_openrouter_error_returns_message():
    respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(429, json={"error": "rate limited"})
    )

    result = await call_openrouter("Hello")
    assert "429" in result
