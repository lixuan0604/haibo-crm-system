from haibo.db.connection import db_cursor
from haibo.db.schema import require_tables
from haibo.services.fixed_expense_service import flatten, load_tree
from haibo.services.money import decimal, parse_year, sum_money
from haibo.services.monthly_service import load_monthly


def get_summary(year):
    year = parse_year(year)
    with db_cursor() as cursor:
        require_tables(cursor)
        tree = load_tree(cursor)
        monthly = load_monthly(cursor, year)
    flat = flatten(tree)
    unpaid_items = [item for item in flat if decimal(item["unpaidAmount"]) > 0]
    unpaid_items.sort(key=lambda item: decimal(item["unpaidAmount"]), reverse=True)
    return {
        "year": year,
        "fixedCount": len(flat),
        "annualAmount": sum_money(item["annualAmount"] for item in flat),
        "paidAmount": sum_money(item["paidAmount"] for item in flat),
        "unpaidAmount": sum_money(item["unpaidAmount"] for item in unpaid_items),
        "unpaidCount": len(unpaid_items),
        "monthlyTotal": monthly["total"],
        "recordedMonths": monthly["recordedMonths"],
        "monthTotals": monthly["monthTotals"],
        "unpaidPreview": [
            {
                "id": item["id"],
                "name": item["name"],
                "parentName": item["parentName"],
                "periodText": item["periodText"],
                "unpaidAmount": item["unpaidAmount"],
            }
            for item in unpaid_items
        ],
    }
