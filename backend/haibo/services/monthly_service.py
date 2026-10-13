from decimal import Decimal

from haibo.db.connection import db_cursor
from haibo.db.schema import require_tables
from haibo.repositories import monthly_repository as repo
from haibo.services.money import decimal, money, parse_month, parse_year, sum_money


def fetch_monthly(year):
    year = parse_year(year)
    with db_cursor() as cursor:
        require_tables(cursor)
        return load_monthly(cursor, year)


def load_monthly(cursor, year):
    categories = repo.list_categories(cursor)
    cells = [
        {
            "month": row["month_no"],
            "category": row["category"],
            "amount": None if row["amount"] is None else decimal(row["amount"]),
        }
        for row in repo.fetch_cells(cursor, year)
    ]
    totals = []
    recorded_months = 0
    recorded_total = Decimal("0.00")
    for month in range(1, 13):
        month_cells = [cell for cell in cells if cell["month"] == month and cell["amount"] is not None]
        if not month_cells:
            totals.append({"month": month, "total": None})
            continue
        recorded_months += 1
        month_total = sum_money(cell["amount"] for cell in month_cells)
        recorded_total += decimal(month_total)
        totals.append({"month": month, "total": month_total})
    return {
        "year": year,
        "categories": categories,
        "cells": cells,
        "years": repo.list_years(cursor),
        "monthTotals": totals,
        "recordedMonths": recorded_months,
        "total": recorded_total.quantize(Decimal("0.01")),
    }


def save_monthly_cell(data):
    year = parse_year(data.get("year"))
    month = parse_month(data.get("month"))
    category = str(data.get("category") or "").strip()
    if not category:
        raise ValueError("请选择科目")
    raw_amount = data.get("amount")
    amount = None if raw_amount is None or raw_amount == "" else money(raw_amount, "金额")

    with db_cursor() as cursor:
        require_tables(cursor)
        row = repo.find_category(cursor, category)
        if row is None:
            raise ValueError("这个科目还不存在")
        if amount is None:
            repo.delete_cell(cursor, year, month, row["id"])
        else:
            repo.upsert_cell(cursor, year, month, row["id"], amount)


def add_category(name):
    name = str(name or "").strip()
    if not name:
        raise ValueError("请填写科目名称")
    if len(name) > 64:
        raise ValueError("科目名称太长")
    try:
        with db_cursor() as cursor:
            require_tables(cursor)
            return repo.insert_category(cursor, name, repo.next_sort_order(cursor))
    except Exception as exc:
        if repo.is_duplicate(exc):
            raise ValueError("这个科目已经有了") from exc
        raise


def replace_imported(cursor, year, categories, cells):
    repo.delete_year(cursor, year)
    for index, name in enumerate(categories, start=1):
        repo.insert_category_ignore(cursor, name, index)
    ids = repo.category_map(cursor)
    for cell in cells:
        category_id = ids.get(cell["category"])
        if category_id is None:
            continue
        repo.upsert_cell(cursor, year, cell["month"], category_id, cell["amount"])
