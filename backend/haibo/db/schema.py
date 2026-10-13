from pathlib import Path

from haibo.db.connection import db_cursor

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema.sql"


class NeedInit(Exception):
    pass


def split_sql(text):
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    body = "\n".join(lines)
    return [part.strip() for part in body.split(";") if part.strip()]


def tables_ready(cursor):
    cursor.execute("SHOW TABLES LIKE 'fixed_expenses'")
    return cursor.fetchone() is not None


def require_tables(cursor):
    if not tables_ready(cursor):
        raise NeedInit()


def init_database():
    statements = split_sql(SCHEMA_PATH.read_text(encoding="utf-8-sig"))
    with db_cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
