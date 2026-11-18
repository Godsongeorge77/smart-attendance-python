import hashlib
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class AttendanceDatabase:
    def __init__(self, db_path: str = "smart_attendance.db"):
        self.db_path = db_path
        self._init_db()
        self._seed_defaults()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS auth_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    matric_no TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    level TEXT NOT NULL,
                    enrolled_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS attendance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    matric_no TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time_in TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, date)
                )
            """)
            conn.commit()

    def _seed_defaults(self):
        with self._connect() as conn:
            auth_count = conn.execute("SELECT COUNT(*) FROM auth_accounts").fetchone()[0]
            if auth_count == 0:
                accounts = [
                    ("admin", _hash_password("admin123"), "System Administrator", "Admin"),
                    ("lecturer", _hash_password("staff123"), "Dr. Adebayo Kunle", "Staff"),
                ]
                conn.executemany(
                    "INSERT INTO auth_accounts (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                    accounts,
                )

            user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if user_count == 0:
                seed_users = [
                    ("CSC/2022/1042", "Chinedu Okafor", "Computer Science", "400L", "2026-09-10"),
                    ("CSC/2022/1089", "Amina Yusuf", "Computer Science", "400L", "2026-09-11"),
                    ("EEE/2023/0412", "Tobi Adeyemi", "Electrical Engineering", "300L", "2026-09-12"),
                ]
                conn.executemany(
                    "INSERT INTO users (matric_no, full_name, department, level, enrolled_at) VALUES (?, ?, ?, ?, ?)",
                    seed_users,
                )
            conn.commit()

    # -------------------- Authentication --------------------
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, full_name, role FROM auth_accounts WHERE username = ? AND password_hash = ?",
                (username.strip().lower(), _hash_password(password)),
            ).fetchone()
            return dict(row) if row else None

    def register_account(self, username: str, password: str, full_name: str, role: str = "Staff") -> Tuple[bool, str]:
        uname = username.strip().lower()
        if len(uname) < 3 or len(password) < 4:
            return False, "Username must be at least 3 characters and password at least 4 characters."
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO auth_accounts (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                    (uname, _hash_password(password), full_name.strip(), role),
                )
                conn.commit()
            return True, f"Account '{uname}' created successfully. You can now sign in."
        except sqlite3.IntegrityError:
            return False, f"Username '{uname}' is already taken."

    # -------------------- Enrolled Profiles --------------------
    def get_users(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]

    def add_user(self, matric_no: str, full_name: str, department: str, level: str) -> Tuple[bool, str]:
        today_str = date.today().isoformat()
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (matric_no, full_name, department, level, enrolled_at) VALUES (?, ?, ?, ?, ?)",
                    (matric_no.strip().upper(), full_name.strip(), department.strip(), level, today_str),
                )
                conn.commit()
            return True, f"Enrolled {full_name.strip()} ({matric_no.strip().upper()}) successfully."
        except sqlite3.IntegrityError:
            return False, f"Matric / Staff ID '{matric_no.strip().upper()}' already exists."

    def delete_user(self, user_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

    # -------------------- Attendance Logs --------------------
    def get_records(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM attendance_records ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]

    def log_attendance(self, user: Dict, confidence: float) -> Tuple[bool, str]:
        today_str = date.today().isoformat()
        now = datetime.now()
        time_in = now.strftime("%H:%M:%S")
        status = "Late" if now.hour >= 9 else "Present"

        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO attendance_records
                    (user_id, matric_no, full_name, department, date, time_in, confidence, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user["id"],
                        user["matric_no"],
                        user["full_name"],
                        user["department"],
                        today_str,
                        time_in,
                        round(confidence, 1),
                        status,
                    ),
                )
                conn.commit()
            return True, f"Attendance verified for {user['full_name']} ({confidence:.1f}% match) — Status: {status}."
        except sqlite3.IntegrityError:
            return False, f"{user['full_name']} is already marked present for {today_str}."
