import pymysql
from flask import Blueprint

from config import IMPORT_YEAR, database_configured
from haibo.db.connection import db_cursor, mysql_message
from haibo.db.schema import tables_ready
from haibo.http import json_response

bp = Blueprint("health", __name__)


@bp.get("/api/health")
def health():
    payload = {"importYear": IMPORT_YEAR}
    if not database_configured():
        payload.update({"ok": False, "database": "unconfigured"})
        return json_response(payload)
    try:
        with db_cursor() as cursor:
            ready = tables_ready(cursor)
        payload.update({"ok": ready, "database": "ready" if ready else "empty"})
        return json_response(payload)
    except pymysql.MySQLError as exc:
        payload.update({"ok": False, "database": "unreachable", "error": mysql_message(exc)})
        return json_response(payload)
