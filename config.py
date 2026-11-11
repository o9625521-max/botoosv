import os
from dotenv import load_dotenv

load_dotenv()

def parse_admin_ids(raw: str):
    if not raw:
        return []
    ids = []
    for item in raw.split(","):
        item = item.strip()
        if item.isdigit():
            ids.append(int(item))
    return ids


def parse_chat_id(raw: str):
    if not raw:
        return None
    raw = raw.strip()
    if raw.lstrip("-").isdigit():
        return int(raw)
    return None


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = parse_admin_ids(os.getenv("ADMIN_IDS", ""))
DB_PATH = os.getenv("DB_PATH", "bot.db")
TEAM_CHAT_ID = parse_chat_id(os.getenv("TEAM_CHAT_ID", ""))
START_BONUS = float(os.getenv("START_BONUS", "0"))

NS1 = os.getenv("NS1", "")
NS2 = os.getenv("NS2", "")
CF_NS1 = os.getenv("CF_NS1", "")
CF_NS2 = os.getenv("CF_NS2", "")
TEAM_CHAT_INVITE_LINK = os.getenv("TEAM_CHAT_INVITE_LINK", "")
PAYOUTS_CHANNEL_INVITE_LINK = os.getenv("PAYOUTS_CHANNEL_INVITE_LINK", "")
PAYOUTS_CHANNEL_ID = parse_chat_id(os.getenv("PAYOUTS_CHANNEL_ID", ""))
