import os
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent / ".env"


def _load_env_file(path):
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file(_ENV_PATH)


def _setting(name, default=""):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def get_mysql_config():
    port = _setting("MYSQL_PORT", "3306")
    return {
        "host": _setting("MYSQL_HOST"),
        "port": int(port),
        "user": _setting("MYSQL_USER"),
        "password": _setting("MYSQL_PASSWORD"),
        "database": _setting("MYSQL_DATABASE"),
        "charset": "utf8mb4",
    }


def database_configured(config=None):
    config = config or get_mysql_config()
    return bool(
        str(config.get("host") or "").strip()
        and str(config.get("user") or "").strip()
        and str(config.get("database") or "").strip()
    )


IMPORT_YEAR = int(_setting("MYSQL_IMPORT_YEAR", "2026"))
