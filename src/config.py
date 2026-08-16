"""Shared paths, institution list, and credential loading.

Credentials are never hardcoded here. Both the MySQL password and the BEA key (if
ever needed again) are read at runtime from secrets/, which is excluded from upload.
"""
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUT = PROJECT_ROOT / "output"
CHARTS = OUTPUT / "charts"
QUERIES = OUTPUT / "queries"
SECRETS = PROJECT_ROOT / "secrets"

# The five institutions under study. Verified against HD2025 in Task 3.
INSTITUTIONS = {
    221768: "University of Tennessee at Martin",
    157401: "Murray State University",
    220057: "Dyersburg State Community College",
    220400: "Jackson State Community College",
    107327: "Arkansas Northeastern College",
}

# Short labels for chart axes, where full names do not fit.
SHORT_NAMES = {
    221768: "UT Martin",
    157401: "Murray State",
    220057: "Dyersburg State",
    220400: "Jackson State",
    107327: "Ark. Northeastern",
}

# host is "localhost", not the literal "127.0.0.1": the server binds IPv6 only,
# and "localhost" resolves to whichever stack answers.
MYSQL = {
    "host": "localhost",
    "port": 3306,
    "user": "ipeds_app",
    "database": "utm_ipeds",
}


def mysql_password() -> str:
    """Read the ipeds_app password from the environment, falling back to secrets/."""
    env = os.environ.get("MYSQL_APP_PASSWORD")
    if env and env.strip():
        return env.strip()
    keyfile = SECRETS / "mysql_app_password.txt"
    if keyfile.exists():
        text = keyfile.read_text(encoding="utf-8").strip()
        if text:
            return text
    raise RuntimeError(
        "No MySQL password found. Set MYSQL_APP_PASSWORD or create "
        "secrets/mysql_app_password.txt"
    )


def bea_api_key() -> str:
    """Read the BEA key. Unused in the current design (BEA was dropped, see spec 5)."""
    env = os.environ.get("BEA_API_KEY")
    if env and env.strip():
        return env.strip()
    keyfile = SECRETS / "bea_api_key.txt"
    if keyfile.exists():
        text = keyfile.read_text(encoding="utf-8").strip()
        if text:
            return text
    raise RuntimeError("No BEA API key found in secrets/bea_api_key.txt")
