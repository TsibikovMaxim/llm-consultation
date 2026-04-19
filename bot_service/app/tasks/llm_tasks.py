import asyncio

from app.infra.celery_app import celery_app

LOADING_FRAMES = [
    "Генерирую ответ...\n[==        ] 20%",
    "Генерирую ответ...\n[====      ] 40%",
    "Генерирую ответ...\n[======    ] 60%",
    "Генерирую ответ...\n[========  ] 80%",
    "Генерирую ответ...\n[==========] 99%",
]


@celery_app.task(name="app.tasks.llm_tasks.llm_request")
def llm_request(tg_chat_id: int, prompt: str, loading_message_id: int | None = None) -> None:
    from aiogram import Bot

    from app.core.config import settings
    from app.services.openrouter_client import call_openrouter

    async def _run():
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        try:
            for frame in LOADING_FRAMES:
                await asyncio.sleep(0.8)
                try:
                    if loading_message_id:
                        await bot.edit_message_text(
                            chat_id=tg_chat_id,
                            message_id=loading_message_id,
                            text=frame,
                        )
                except Exception:
                    pass

            response_text = await call_openrouter(prompt)

            if loading_message_id:
                await bot.edit_message_text(
                    chat_id=tg_chat_id,
                    message_id=loading_message_id,
                    text=response_text,
                )
            else:
                await bot.send_message(chat_id=tg_chat_id, text=response_text)

        except Exception as e:
            error_text = f"Error: {e}"
            try:
                if loading_message_id:
                    await bot.edit_message_text(
                        chat_id=tg_chat_id,
                        message_id=loading_message_id,
                        text=error_text,
                    )
                else:
                    await bot.send_message(chat_id=tg_chat_id, text=error_text)
            except Exception:
                pass
        finally:
            await bot.session.close()

    asyncio.run(_run())
