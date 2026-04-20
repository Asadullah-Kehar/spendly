"""
manage.py — development management script for Spendly

Usage:
    python manage.py init-db     # create tables (safe to re-run)
    python manage.py seed-db     # insert sample data (idempotent)
    python manage.py reset-db    # drop all tables → init → seed
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_db, init_db, seed_db


def reset_db():
    conn = get_db()
    conn.executescript("""
        DROP TABLE IF EXISTS expenses;
        DROP TABLE IF EXISTS categories;
        DROP TABLE IF EXISTS users;
    """)
    conn.commit()
    conn.close()
    init_db()
    seed_db()
    print("Database reset complete.")


def main():
    parser = argparse.ArgumentParser(description="Spendly dev management commands")
    parser.add_argument("command", choices=["init-db", "seed-db", "reset-db"])
    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
    elif args.command == "seed-db":
        seed_db()
    elif args.command == "reset-db":
        reset_db()


if __name__ == "__main__":
    main()
