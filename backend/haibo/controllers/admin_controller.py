from flask import Blueprint

from haibo.db.schema import init_database
from haibo.http import api, json_response
from haibo.services.import_service import import_excel

bp = Blueprint("admin", __name__)


@bp.post("/api/admin/init")
@api
def admin_init():
    init_database()
    return json_response({"ok": True})


@bp.post("/api/admin/import-excel")
@api
def admin_import_excel():
    return json_response(import_excel())
