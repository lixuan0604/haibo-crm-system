from flask import Blueprint, request

from config import IMPORT_YEAR
from haibo.http import api, json_response, request_json
from haibo.services.monthly_service import add_category, fetch_monthly, save_monthly_cell

bp = Blueprint("monthly", __name__)


@bp.get("/api/monthly")
@api
def monthly():
    year = request.args.get("year", IMPORT_YEAR)
    return json_response(fetch_monthly(year))


@bp.put("/api/monthly")
@api
def update_monthly():
    save_monthly_cell(request_json())
    return json_response({"ok": True})


@bp.post("/api/monthly-categories")
@api
def create_category():
    data = request_json()
    category_id = add_category(data.get("name"))
    return json_response({"id": category_id}, 201)
