import csv
import json
import logging
from datetime import date, datetime
from decimal import Decimal
from functools import wraps
from io import StringIO
from urllib.parse import quote

import pymysql
from flask import Response, request

from haibo.db.connection import DatabaseNotConfigured, mysql_message
from haibo.db.schema import NeedInit


class DecimalEncoder(json.JSONEncoder):
    def default(self, value):
        if isinstance(value, Decimal):
            return format(value.quantize(Decimal("0.01")), "f")
        if isinstance(value, datetime):
            return value.isoformat(sep=" ", timespec="seconds")
        if isinstance(value, date):
            return value.isoformat()
        return super().default(value)


def json_response(data, status=200):
    payload = json.dumps(data, ensure_ascii=False, cls=DecimalEncoder)
    return Response(payload, status=status, mimetype="application/json; charset=utf-8")


def json_error(message, code, status):
    return json_response({"error": message, "code": code}, status)


def api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseNotConfigured:
            return json_error("数据库尚未配置，请先填写 backend/config.py 里的阿里云 MySQL", "DB_NOT_CONFIGURED", 503)
        except NeedInit:
            return json_error("数据表还没有初始化", "NEED_INIT", 400)
        except ValueError as exc:
            return json_error(str(exc), "BAD_REQUEST", 400)
        except FileNotFoundError:
            return json_error("没有找到海博固定费用.xlsx", "NO_EXCEL", 400)
        except pymysql.err.ProgrammingError as exc:
            logging.exception("mysql programming error")
            if exc.args and exc.args[0] == 1146:
                return json_error("数据表还没有初始化", "NEED_INIT", 400)
            return json_error(mysql_message(exc), "DB_ERROR", 500)
        except pymysql.err.OperationalError as exc:
            logging.exception("mysql operational error")
            return json_error(mysql_message(exc), "DB_ERROR", 503)
        except pymysql.MySQLError as exc:
            logging.exception("mysql error")
            return json_error(mysql_message(exc), "DB_ERROR", 500)

    return wrapper


def request_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("请求格式不正确")
    return data


def csv_response(filename, header, rows):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    response = Response("\ufeff" + buffer.getvalue(), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
    return response
