import os

from dotenv import load_dotenv

load_dotenv()


def _format_server(server: str) -> str:
    if not server:
        return server
    lowered = server.lower()
    if "database.windows.net" in lowered and not lowered.startswith("tcp:"):
        return f"tcp:{server},1433"
    return server


def build_connection_string(database: str | None = None) -> str:
    server = _format_server(os.getenv("DB_SERVER", ""))
    db_name = database or os.getenv("DB_DATABASE", "")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    user = os.getenv("DB_USER", "").strip()
    password = os.getenv("DB_PASSWORD", "")

    if user and password:
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={db_name};"
            f"UID={user};"
            f"PWD={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
        )

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={db_name};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )


def uses_sql_authentication() -> bool:
    return bool(os.getenv("DB_USER", "").strip() and os.getenv("DB_PASSWORD"))
