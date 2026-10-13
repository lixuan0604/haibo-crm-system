from decimal import Decimal

from haibo.db.connection import db_cursor
from haibo.repositories import fixed_expense_repository as repo
from haibo.services.money import CENT, blank, decimal, money, optional_int, parse_date, sum_money


def list_fixed_expenses():
    with db_cursor() as cursor:
        return load_tree(cursor)


def load_tree(cursor):
    repo.ensure_ready(cursor)
    payments = {}
    for row in repo.fetch_payment_rows(cursor):
        payments.setdefault(row["expense_id"], []).append(
            {
                "id": row["id"],
                "seqNo": row["seq_no"],
                "amount": decimal(row["amount"]),
                "paidOn": row["paid_on"],
                "remark": row["remark"],
            }
        )

    nodes = {}
    ordered = []
    for row in repo.fetch_expense_rows(cursor):
        annual = decimal(row["annual_amount"])
        paid = decimal(row["paid_amount"])
        node = {
            "id": row["id"],
            "parentId": row["parent_id"],
            "name": row["name"],
            "note": row["note"],
            "periodText": row["period_text"],
            "annualAmount": annual,
            "paidAmount": paid,
            "unpaidAmount": (annual - paid).quantize(CENT),
            "payments": payments.get(row["id"], []),
            "children": [],
        }
        nodes[row["id"]] = node
        ordered.append(node)

    roots = []
    for node in ordered:
        parent = nodes.get(node["parentId"])
        if parent is not None and parent is not node:
            parent["children"].append(node)
        else:
            roots.append(node)
    return roots


def save_expense(data, expense_id=None):
    name = str(data.get("name") or "").strip()
    if not name:
        raise ValueError("请填写费用名称")
    annual = money(data.get("annualAmount"), "年度金额")
    if annual < 0:
        raise ValueError("年度金额不能是负数")
    parent_id = optional_int(data.get("parentId"))
    note = blank(data.get("note"))
    period = blank(data.get("periodText"))
    payments = data.get("payments") or []
    if not isinstance(payments, list):
        raise ValueError("付款记录格式不正确")

    with db_cursor() as cursor:
        repo.ensure_ready(cursor)
        _validate_parent(cursor, parent_id, expense_id)
        if expense_id is None:
            expense_id = repo.insert_expense(
                cursor,
                parent_id,
                name,
                note,
                period,
                annual,
                repo.next_sort_order(cursor),
            )
        else:
            if repo.find_expense(cursor, expense_id) is None:
                raise ValueError("这项费用不存在")
            repo.update_expense(cursor, expense_id, parent_id, name, note, period, annual)
            repo.delete_payments(cursor, expense_id)
        _replace_payments(cursor, expense_id, payments)
    return expense_id


def delete_expense(expense_id):
    with db_cursor() as cursor:
        repo.ensure_ready(cursor)
        if repo.find_expense(cursor, expense_id) is None:
            raise ValueError("这项费用不存在")
        repo.delete_expense(cursor, expense_id)


def unpaid_report():
    items = [item for item in flatten(list_fixed_expenses()) if decimal(item["unpaidAmount"]) > 0]
    items.sort(key=lambda item: decimal(item["unpaidAmount"]), reverse=True)
    return {
        "count": len(items),
        "unpaidAmount": sum_money(item["unpaidAmount"] for item in items),
        "items": items,
    }


def flatten(nodes, parent_name=""):
    rows = []
    for node in nodes:
        rows.append(
            {
                "id": node["id"],
                "parentName": parent_name,
                "name": node["name"],
                "note": node["note"],
                "periodText": node["periodText"],
                "annualAmount": node["annualAmount"],
                "paidAmount": node["paidAmount"],
                "unpaidAmount": node["unpaidAmount"],
                "payments": node["payments"],
            }
        )
        rows.extend(flatten(node["children"], node["name"]))
    return rows


def _validate_parent(cursor, parent_id, expense_id):
    if parent_id is None:
        return
    if expense_id is not None and parent_id == expense_id:
        raise ValueError("不能把自己设为上级")
    parent = repo.find_expense(cursor, parent_id)
    if parent is None:
        raise ValueError("上级费用不存在")
    if parent["parent_id"] is not None:
        raise ValueError("只支持一层上下级")
    if expense_id is not None and repo.count_children(cursor, expense_id):
        raise ValueError("这项下面还有子项，不能再挂到别的费用下")


def _replace_payments(cursor, expense_id, payments):
    seq_no = 1
    for payment in payments:
        raw_amount = payment.get("amount")
        if raw_amount is None or raw_amount == "":
            continue
        amount = money(raw_amount, "付款金额")
        if amount <= 0:
            raise ValueError("付款金额要大于 0")
        repo.insert_payment(
            cursor,
            expense_id,
            seq_no,
            amount,
            parse_date(payment.get("paidOn")),
            blank(payment.get("remark")),
        )
        seq_no += 1


def replace_imported(cursor, items):
    repo.clear_all(cursor)
    row_to_id = {}
    for item in items:
        if item["parent_row"] is not None:
            continue
        new_id = repo.insert_expense(
            cursor,
            None,
            item["name"],
            item["note"],
            item["period_text"],
            item["annual_amount"],
            item["sort_order"],
            item["source_row"],
        )
        row_to_id[item["source_row"]] = new_id
        _replace_payments(cursor, new_id, item["payments"])
    for item in items:
        if item["parent_row"] is None:
            continue
        new_id = repo.insert_expense(
            cursor,
            row_to_id.get(item["parent_row"]),
            item["name"],
            item["note"],
            item["period_text"],
            item["annual_amount"],
            item["sort_order"],
            item["source_row"],
        )
        _replace_payments(cursor, new_id, item["payments"])
