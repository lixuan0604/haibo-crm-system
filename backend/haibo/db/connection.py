from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor

from config import database_configured, get_mysql_config


class DatabaseNotConfigured(Exception):
    pass


def connect():
    config = get_mysql_config()
    if not database_configured(config):
        raise DatabaseNotConfigured("数据库尚未配置")
    return pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        charset=config["charset"],
        cursorclass=DictCursor,
        autocommit=False,
        connect_timeout=5,
        read_timeout=30,
        write_timeout=30,
    )


@contextmanager
def db_cursor():
    connection = connect()
    try:
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def mysql_message(error):
    if getattr(error, "args", None) and len(error.args) >= 2:
        return f"数据库操作失败：{error.args[1]}"
    return "数据库操作失败"
