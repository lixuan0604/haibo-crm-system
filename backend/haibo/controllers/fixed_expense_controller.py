from flask import Blueprint, request

from config import IMPORT_YEAR
from haibo.http import api, json_response, request_json
from haibo.services.fixed_expense_service import delete_expense, list_fixed_expenses, save_expense
from haibo.services.summary_service import get_summary

bp = Blueprint("fixed_expenses", __name__)


@bp.get("/api/summary")
@api
def summary():
    year = request.args.get("year", IMPORT_YEAR)
    return json_response(get_summary(year))


@bp.get("/api/fixed-expenses")
@api
def fixed_expenses():
    return json_response({"items": list_fixed_expenses()})


@bp.post("/api/fixed-expenses")
@api
def create_fixed_expense():
    expense_id = save_expense(request_json())
    return json_response({"id": expense_id}, 201)


@bp.put("/api/fixed-expenses/<int:expense_id>")
@api
def update_fixed_expense(expense_id):
    save_expense(request_json(), expense_id)
    return json_response({"id": expense_id})


@bp.delete("/api/fixed-expenses/<int:expense_id>")
@api
def remove_fixed_expense(expense_id):
    delete_expense(expense_id)
    return json_response({"ok": True})
