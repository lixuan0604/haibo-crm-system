from decimal import Decimal

from flask import Blueprint, request

from config import IMPORT_YEAR
from haibo.http import api, csv_response, json_response
from haibo.services.fixed_expense_service import unpaid_report
from haibo.services.monthly_service import fetch_monthly

bp = Blueprint("reports", __name__)


@bp.get("/api/reports/unpaid")
@api
def report_unpaid():
    return json_response(unpaid_report())


@bp.get("/api/reports/unpaid.csv")
@api
def report_unpaid_csv():
    report = unpaid_report()
    rows = [
        [
            item["parentName"] or "",
            item["name"],
            item["periodText"] or "",
            item["note"] or "",
            item["annualAmount"],
            item["paidAmount"],
            item["unpaidAmount"],
        ]
        for item in report["items"]
    ]
    rows.append(["", "合计", "", "", "", "", report["unpaidAmount"]])
    return csv_response("未付清单.csv", ["上级", "费用", "起止日期", "说明", "年度金额", "已付", "未付"], rows)


@bp.get("/api/reports/monthly.csv")
@api
def report_monthly_csv():
    year = int(request.args.get("year", IMPORT_YEAR))
    raw_month = request.args.get("month")
    month = int(raw_month) if raw_month else None
    if month is not None and (month < 1 or month > 12):
        raise ValueError("月份不正确")
    data = fetch_monthly(year)
    header = ["月份", *data["categories"], "合计"]
    rows = []
    for month_no in range(1, 13):
        if month and month_no != month:
            continue
        values = [_cell_amount(data["cells"], month_no, category) for category in data["categories"]]
        total = _row_total(values)
        rows.append([f"{month_no}月", *[_plain(value) for value in values], _plain(total)])
    filename = f"{year}年{month}月费用.csv" if month else f"{year}年每月费用.csv"
    return csv_response(filename, header, rows)


def _cell_amount(cells, month, category):
    for cell in cells:
        if cell["month"] == month and cell["category"] == category:
            return cell["amount"]
    return None


def _row_total(values):
    numbers = [value for value in values if value is not None]
    if not numbers:
        return None
    return format(sum((Decimal(value) for value in numbers), Decimal("0.00")).quantize(Decimal("0.01")), "f")


def _plain(value):
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return format(value.quantize(Decimal("0.01")), "f")
    return value
