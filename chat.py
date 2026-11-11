from aiogram import Bot
from database import get_setting


async def _team_chat_id():
    raw = await get_setting("team_chat_id", "")
    if raw.lstrip("-").isdigit():
        return int(raw)
    return None


async def ban_in_team_chat(bot: Bot, user_id: int):
    chat_id = await _team_chat_id()
    if not chat_id:
        return False, "TEAM_CHAT_ID not configured"
    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        return True, None
    except Exception as e:
        return False, str(e)


async def unban_in_team_chat(bot: Bot, user_id: int):
    chat_id = await _team_chat_id()
    if not chat_id:
        return False, "TEAM_CHAT_ID not configured"
    try:
        await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
        return True, None
    except Exception as e:
        return False, str(e)
