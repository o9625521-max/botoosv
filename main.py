import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import TelegramObject
from typing import Callable, Any, Awaitable
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, get_user, get_application, update_username
from chat import ban_in_team_chat, unban_in_team_chat
from handlers import start, menu, countries, wallet, referral, other, admin, application, site_logs, log_menu
from handlers.application import ApplicationState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def is_admin_user(user_id: int, db_user: dict = None):
    if user_id in ADMIN_IDS:
        return True
    if db_user and db_user.get("role") in ("admin", "tc"):
        return True
    return False


class BanMiddleware:
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = None
        if hasattr(event, "from_user") and event.from_user:
            user = event.from_user
        if user:
            db_user = await get_user(user.id)
            if db_user:
                fresh = user.username or ""
                if (db_user.get("username") or "") != fresh:
                    await update_username(user.id, fresh)
                    db_user["username"] = fresh
            if not is_admin_user(user.id, db_user) and db_user and db_user.get("banned"):
                return None
        return await handler(event, data)


class ApprovalMiddleware:
    """Не пускает в бот людей без одобренной заявки (кроме персонала и админов)."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        # Разрешаем /start, чтобы показать анкету
        if isinstance(event, types.Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)

        # Разрешаем прохождение анкеты по состоянию
        state = data.get("state")
        if state:
            current = await state.get_state()
            if current and current.startswith("ApplicationState:"):
                return await handler(event, data)

        db_user = await get_user(user.id)
        lang = db_user.get("language", "ru") or "ru" if db_user else "ru"

        if db_user:
            role = db_user.get("role", "worker")
            staff = user.id in ADMIN_IDS or role in ("admin", "tc", "vbiver")
            if staff:
                return await handler(event, data)
            application = await get_application(user.id)
            if application and application.get("status") == "approved":
                return await handler(event, data)

        # Блокируем — просим заполнить заявку
        text = "📝 Сначала заполните заявку на вступление в команду."
        bot = data.get("bot")
        if isinstance(event, types.Message):
            await event.answer(text)
        elif isinstance(event, types.CallbackQuery) and bot:
            await bot.send_message(user.id, text)
            await event.answer()
        return None


async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())
    dp.message.middleware(ApprovalMiddleware())
    dp.callback_query.middleware(ApprovalMiddleware())

    dp.include_routers(
        start.router,
        menu.router,
        countries.router,
        wallet.router,
        referral.router,
        other.router,
        admin.router,
        application.router,
        site_logs.router,
        log_menu.router,
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
