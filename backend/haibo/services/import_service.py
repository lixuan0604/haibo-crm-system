from haibo.db.connection import db_cursor
from haibo.db.schema import require_tables
from haibo.services.excel_reader import parse_workbook
from haibo.services.fixed_expense_service import replace_imported as replace_fixed
from haibo.services.monthly_service import replace_imported as replace_monthly


def import_excel():
    parsed = parse_workbook()
    with db_cursor() as cursor:
        require_tables(cursor)
        replace_fixed(cursor, parsed["fixed"])
        replace_monthly(cursor, parsed["year"], parsed["categories"], parsed["monthly"])
    return {
        "fixedCount": len(parsed["fixed"]),
        "paymentCount": sum(len(item["payments"]) for item in parsed["fixed"]),
        "monthlyCount": len(parsed["monthly"]),
        "monthlyYear": parsed["year"],
    }
