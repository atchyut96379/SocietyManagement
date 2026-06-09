import os
from urllib.parse import unquote

from dotenv import load_dotenv

load_dotenv()


def _format_server(server: str) -> str:
    if not server:
        return server
    lowered = server.lower()
    if "database.windows.net" in lowered and not lowered.startswith("tcp:"):
        return f"tcp:{server},1433"
    return server


def parse_database_url(url: str) -> dict | None:
    """
    Parse legacy DATABASE_URL format:
    sqlserver://host:1433;database=mygatesociety;user=sa;password=...;encrypt=true
    """
    if not url or not url.lower().startswith("sqlserver://"):
        return None

    remainder = url[len("sqlserver://"):]
    host_part, _, params_part = remainder.partition(";")

    server = host_part
    if ":" in host_part:
        host, port = host_part.rsplit(":", 1)
        if "database.windows.net" in host.lower():
            server = f"tcp:{host},{port}"
        else:
            server = host

    params: dict[str, str] = {}
    for segment in params_part.split(";"):
        if "=" not in segment:
            continue
        key, value = segment.split("=", 1)
        params[key.strip().lower()] = unquote(value.strip())

    trust_cert = params.get("trustservercertificate", "false").lower() == "true"

    return {
        "server": _format_server(server),
        "database": params.get("database", ""),
        "user": params.get("user", ""),
        "password": params.get("password", ""),
        "trust_server_certificate": trust_cert,
    }


def _connection_parts(database: str | None = None) -> dict:
    parsed = parse_database_url(os.getenv("DATABASE_URL", ""))

    if parsed:
        return {
            "server": parsed["server"],
            "database": database or parsed["database"],
            "user": parsed["user"],
            "password": parsed["password"],
            "trust_server_certificate": parsed["trust_server_certificate"],
        }

    return {
        "server": _format_server(os.getenv("DB_SERVER", "")),
        "database": database or os.getenv("DB_DATABASE", ""),
        "user": os.getenv("DB_USER", "").strip(),
        "password": os.getenv("DB_PASSWORD", ""),
        "trust_server_certificate": os.getenv(
            "DB_TRUST_SERVER_CERTIFICATE", "false"
        ).lower() == "true",
    }


def build_connection_string(database: str | None = None) -> str:
    parts = _connection_parts(database)
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    user = parts["user"]
    password = parts["password"]

    if user and password:
        trust = "yes" if parts["trust_server_certificate"] else "no"
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={parts['server']};"
            f"DATABASE={parts['database']};"
            f"UID={user};"
            f"PWD={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate={trust};"
        )

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={parts['server']};"
        f"DATABASE={parts['database']};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )


def uses_sql_authentication() -> bool:
    parsed = parse_database_url(os.getenv("DATABASE_URL", ""))
    if parsed:
        return bool(parsed["user"] and parsed["password"])
    return bool(os.getenv("DB_USER", "").strip() and os.getenv("DB_PASSWORD"))
