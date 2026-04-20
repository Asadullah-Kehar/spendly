import os
import sqlite3


def get_db(db_path=None):
    if db_path is None:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "spendly.db",
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None):
    conn = get_db(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name  TEXT    NOT NULL,
            email      TEXT    NOT NULL UNIQUE,
            password   TEXT    NOT NULL,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS categories (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL UNIQUE,
            icon TEXT    NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(id),
            title       TEXT    NOT NULL,
            amount      REAL    NOT NULL CHECK (amount > 0),
            date        TEXT    NOT NULL,
            notes       TEXT    NOT NULL DEFAULT '',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
        CREATE INDEX IF NOT EXISTS idx_expenses_date    ON expenses(date);
    """)
    conn.commit()
    conn.close()
    print("Database initialised.")


def seed_db(db_path=None):
    from werkzeug.security import generate_password_hash

    conn = get_db(db_path)
    cursor = conn.cursor()

    if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        print("Database already has data. Skipping seed.")
        conn.close()
        return

    cursor.executemany(
        "INSERT INTO categories (name, icon) VALUES (?, ?)",
        [
            ("Food", "food"),
            ("Travel", "travel"),
            ("Bills", "bills"),
            ("Shopping", "shopping"),
            ("Health", "health"),
            ("Entertainment", "entertainment"),
        ],
    )

    cursor.executemany(
        "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
        [
            ("Nitish Kumar", "nitish@example.com", generate_password_hash("password123")),
            ("Priya Sharma", "priya@example.com", generate_password_hash("password123")),
        ],
    )

    nitish_id = cursor.execute("SELECT id FROM users WHERE email = 'nitish@example.com'").fetchone()[0]
    priya_id  = cursor.execute("SELECT id FROM users WHERE email = 'priya@example.com'").fetchone()[0]

    def cat(name):
        return cursor.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()[0]

    expenses = [
        (nitish_id, cat("Food"),          "Lunch at Haldiram's",   320.00, "2026-04-18", ""),
        (nitish_id, cat("Travel"),        "Ola cab to office",     180.00, "2026-04-17", ""),
        (nitish_id, cat("Bills"),         "Electricity bill",     1450.00, "2026-04-10", ""),
        (nitish_id, cat("Shopping"),      "Myntra order",         2199.00, "2026-04-05", ""),
        (nitish_id, cat("Health"),        "Pharmacy",              340.00, "2026-03-28", ""),
        (nitish_id, cat("Entertainment"), "Hotstar subscription",  299.00, "2026-03-25", ""),
        (nitish_id, cat("Food"),          "Zomato dinner",         450.00, "2026-04-20", ""),
        (nitish_id, cat("Travel"),        "Auto to market",         60.00, "2026-04-19", ""),
        (priya_id,  cat("Food"),          "Breakfast canteen",      85.00, "2026-04-19", ""),
        (priya_id,  cat("Bills"),         "Internet bill",         799.00, "2026-04-08", ""),
        (priya_id,  cat("Shopping"),      "Amazon books",          799.00, "2026-04-15", ""),
        (priya_id,  cat("Health"),        "Doctor consultation",   500.00, "2026-04-12", ""),
        (priya_id,  cat("Travel"),        "Metro card recharge",   500.00, "2026-04-11", ""),
        (priya_id,  cat("Entertainment"), "Movie tickets",         600.00, "2026-04-03", ""),
        (priya_id,  cat("Food"),          "Grocery run",          1200.00, "2026-03-30", ""),
    ]

    cursor.executemany(
        "INSERT INTO expenses (user_id, category_id, title, amount, date, notes) VALUES (?, ?, ?, ?, ?, ?)",
        expenses,
    )

    conn.commit()
    conn.close()
    print("Seed data inserted.")
