import hashlib
import os
import secrets
import sqlite3
import time


APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(APP_DIR, "app.db")
DEFAULT_INVITE_CODE = "DEV-INVITE-001"
DEFAULT_SUPER_LOGIN = "FeluxaTopG"
DEFAULT_SUPER_PASSWORD = "feliks244023"


class AuthStore:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()
        self._ensure_super_admin()
        self._ensure_default_invite()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS invite_codes (
                    code TEXT PRIMARY KEY,
                    is_active INTEGER NOT NULL,
                    used_by TEXT,
                    used_at INTEGER
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    owner_user_id INTEGER NOT NULL,
                    invite_code TEXT UNIQUE NOT NULL,
                    created_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS team_members (
                    team_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    joined_at INTEGER NOT NULL,
                    UNIQUE(team_id, user_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    theme TEXT NOT NULL,
                    hotkey TEXT,
                    sound_path TEXT,
                    system_sound TEXT,
                    volume INTEGER
                )
                """
            )
            self._migrate_user_settings(conn)

    def _migrate_user_settings(self, conn):
        columns = {
            row[1]: row[2]
            for row in conn.execute("PRAGMA table_info(user_settings)").fetchall()
        }
        if "hotkey" not in columns:
            conn.execute("ALTER TABLE user_settings ADD COLUMN hotkey TEXT")
        if "sound_path" not in columns:
            conn.execute("ALTER TABLE user_settings ADD COLUMN sound_path TEXT")
        if "system_sound" not in columns:
            conn.execute("ALTER TABLE user_settings ADD COLUMN system_sound TEXT")
        if "volume" not in columns:
            conn.execute("ALTER TABLE user_settings ADD COLUMN volume INTEGER")

    def _ensure_super_admin(self):
        existing = self.get_user(DEFAULT_SUPER_LOGIN)
        if existing is not None:
            return
        salt = self._generate_salt()
        pwd_hash = self._hash_password(DEFAULT_SUPER_PASSWORD, salt)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (username, password_hash, password_salt, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (DEFAULT_SUPER_LOGIN, pwd_hash, salt, "super_admin", int(time.time())),
            )
        self._ensure_user_settings_by_username(DEFAULT_SUPER_LOGIN)

    def _ensure_default_invite(self):
        if self.get_invite(DEFAULT_INVITE_CODE) is not None:
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO invite_codes (code, is_active, used_by, used_at)
                VALUES (?, 1, NULL, NULL)
                """,
                (DEFAULT_INVITE_CODE,),
            )

    def _ensure_user_settings(self, user_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT user_id FROM user_settings WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO user_settings (user_id, theme, hotkey, sound_path, system_sound, volume) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, "dark", "", "", "Siren", 70),
                )

    def _ensure_user_settings_by_username(self, username):
        user = self.get_user(username)
        if user:
            self._ensure_user_settings(user["id"])

    def _generate_salt(self):
        return secrets.token_hex(16)

    def _hash_password(self, password, salt):
        payload = f"{salt}:{password}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def get_user(self, username):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role, password_hash, password_salt FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "role": row[2],
            "password_hash": row[3],
            "password_salt": row[4],
        }

    def get_user_by_id(self, user_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "username": row[1], "role": row[2]}

    def verify_password(self, user_id, password):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT password_hash, password_salt FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return False
        pwd_hash = self._hash_password(password, row[1])
        return pwd_hash == row[0]

    def get_invite(self, code):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT code, is_active, used_by FROM invite_codes WHERE code = ?",
                (code,),
            ).fetchone()
        if row is None:
            return None
        return {"code": row[0], "is_active": bool(row[1]), "used_by": row[2]}

    def verify_login(self, username, password):
        user = self.get_user(username)
        if user is None:
            return None
        pwd_hash = self._hash_password(password, user["password_salt"])
        if pwd_hash != user["password_hash"]:
            return None
        self._ensure_user_settings(user["id"])
        return {"id": user["id"], "username": user["username"], "role": user["role"]}

    def register_user(self, username, password, invite_code):
        invite = self.get_invite(invite_code)
        if invite is None or not invite["is_active"]:
            return False, "Invalid invite code."
        if self.get_user(username) is not None:
            return False, "Login already exists."

        salt = self._generate_salt()
        pwd_hash = self._hash_password(password, salt)
        now = int(time.time())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (username, password_hash, password_salt, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, pwd_hash, salt, "user", now),
            )
            conn.execute(
                """
                UPDATE invite_codes
                SET is_active = 0, used_by = ?, used_at = ?
                WHERE code = ?
                """,
                (username, now, invite_code),
            )
            conn.execute(
                "INSERT INTO user_settings (user_id, theme, hotkey, sound_path, system_sound, volume) VALUES ((SELECT id FROM users WHERE username = ?), ?, ?, ?, ?, ?)",
                (username, "dark", "", "", "Siren", 70),
            )
        return True, "Account created."

    def get_user_theme(self, user_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT theme FROM user_settings WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return row[0] if row else "dark"

    def set_user_theme(self, user_id, theme):
        theme = theme if theme in ("dark", "light") else "dark"
        with self._connect() as conn:
            conn.execute(
                "UPDATE user_settings SET theme = ? WHERE user_id = ?",
                (theme, user_id),
            )

    def get_user_settings(self, user_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT theme, hotkey, sound_path, system_sound, volume FROM user_settings WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        if not row:
            return {
                "theme": "dark",
                "hotkey": "",
                "sound_path": "",
                "system_sound": "Siren",
                "volume": 70,
            }
        return {
            "theme": row[0],
            "hotkey": row[1] or "",
            "sound_path": row[2] or "",
            "system_sound": row[3] or "Siren",
            "volume": row[4] if row[4] is not None else 70,
        }

    def set_user_settings(self, user_id, hotkey, sound_path, system_sound, volume):
        with self._connect() as conn:
            conn.execute(
                "UPDATE user_settings SET hotkey = ?, sound_path = ?, system_sound = ?, volume = ? WHERE user_id = ?",
                (hotkey or "", sound_path or "", system_sound or "Siren", int(volume), user_id),
            )

    def update_username(self, user_id, new_username):
        if self.get_user(new_username) is not None:
            return False, "Login already exists."
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET username = ? WHERE id = ?",
                (new_username, user_id),
            )
        return True, "Login updated."

    def update_password(self, user_id, new_password):
        salt = self._generate_salt()
        pwd_hash = self._hash_password(new_password, salt)
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?",
                (pwd_hash, salt, user_id),
            )
        return True, "Password updated."

    def generate_invite(self):
        code = f"INV-{secrets.token_hex(4)}"
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO invite_codes (code, is_active, used_by, used_at)
                VALUES (?, 1, NULL, NULL)
                """,
                (code,),
            )
        return code

    def _user_has_team(self, user_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT team_id FROM team_members WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return row is not None

    def create_team(self, user_id, name, description):
        if self._user_has_team(user_id):
            return False, "User already in a team.", None
        invite_code = f"TEAM-{secrets.token_hex(4)}"
        now = int(time.time())
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO teams (name, description, owner_user_id, invite_code, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, description, user_id, invite_code, now),
            )
            team_id = cursor.lastrowid
            conn.execute(
                """
                INSERT INTO team_members (team_id, user_id, role, joined_at)
                VALUES (?, ?, ?, ?)
                """,
                (team_id, user_id, "owner", now),
            )
        return True, "Team created.", team_id

    def get_team_by_invite(self, invite_code):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, description, owner_user_id, invite_code FROM teams WHERE invite_code = ?",
                (invite_code,),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "owner_user_id": row[3],
            "invite_code": row[4],
        }

    def join_team(self, user_id, invite_code):
        if self._user_has_team(user_id):
            return False, "User already in a team.", None
        team = self.get_team_by_invite(invite_code)
        if team is None:
            return False, "Invalid invite code.", None
        now = int(time.time())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO team_members (team_id, user_id, role, joined_at)
                VALUES (?, ?, ?, ?)
                """,
                (team["id"], user_id, "user", now),
            )
        return True, "Joined team.", team["id"]

    def list_teams_for_user(self, user_id):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT t.id, t.name, t.description, t.owner_user_id, t.invite_code
                FROM teams t
                JOIN team_members tm ON tm.team_id = t.id
                WHERE tm.user_id = ?
                """,
                (user_id,),
            ).fetchall()
        teams = []
        for row in rows:
            teams.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "owner_user_id": row[3],
                    "invite_code": row[4],
                }
            )
        return teams

    def get_team_members(self, team_id):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT u.id, u.username, tm.role
                FROM team_members tm
                JOIN users u ON u.id = tm.user_id
                WHERE tm.team_id = ?
                ORDER BY
                    CASE tm.role
                        WHEN 'owner' THEN 1
                        WHEN 'admin' THEN 2
                        WHEN 'user' THEN 3
                        ELSE 4
                    END,
                    u.username ASC
                """,
                (team_id,),
            ).fetchall()
        members = []
        for row in rows:
            members.append({"user_id": row[0], "username": row[1], "role": row[2]})
        return members

    def get_member_role(self, team_id, user_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT role FROM team_members WHERE team_id = ? AND user_id = ?",
                (team_id, user_id),
            ).fetchone()
        return row[0] if row else None

    def generate_team_invite(self, team_id):
        invite_code = f"TEAM-{secrets.token_hex(4)}"
        with self._connect() as conn:
            conn.execute(
                "UPDATE teams SET invite_code = ? WHERE id = ?",
                (invite_code, team_id),
            )
        return invite_code

    def remove_member(self, team_id, user_id):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM team_members WHERE team_id = ? AND user_id = ?",
                (team_id, user_id),
            )

    def leave_team(self, team_id, user_id):
        self.remove_member(team_id, user_id)
