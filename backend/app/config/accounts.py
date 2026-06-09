ACCOUNT_MAINTENANCE = "Maintenance"
ACCOUNT_CORPUS = "Corpus"

VALID_ACCOUNTS = {ACCOUNT_MAINTENANCE, ACCOUNT_CORPUS}


def normalize_account(value: str | None, default: str = ACCOUNT_MAINTENANCE) -> str:
    if not value:
        return default
    cleaned = value.strip().title()
    if cleaned == "Corpus":
        return ACCOUNT_CORPUS
    return ACCOUNT_MAINTENANCE
