from datetime import date, datetime
from decimal import Decimal, InvalidOperation

CENT = Decimal("0.01")


def money(value, field):
    if value is None or value == "":
        raise ValueError(f"请填写{field}")
    if isinstance(value, str):
        value = value.replace(",", "").replace("，", "").strip()
    try:
        amount = Decimal(str(value)).quantize(CENT)
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field}不是有效金额")
    return amount


def decimal(value):
    return Decimal(str(value or 0)).quantize(CENT)


def sum_money(values):
    total = Decimal("0.00")
    for value in values:
        total += decimal(value)
    return total.quantize(CENT)


def blank(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def optional_int(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError("上级费用不正确")


def parse_year(value):
    try:
        year = int(value)
    except (TypeError, ValueError):
        raise ValueError("年份不正确")
    if year < 2000 or year > 2100:
        raise ValueError("年份不正确")
    return year


def parse_month(value):
    try:
        month = int(value)
    except (TypeError, ValueError):
        raise ValueError("月份不正确")
    if month < 1 or month > 12:
        raise ValueError("月份不正确")
    return month


def parse_date(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("付款日期格式应为 YYYY-MM-DD")
