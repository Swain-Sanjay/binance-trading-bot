from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from binance.client import Client
from dotenv import load_dotenv

from bot.logging_config import setup_logging

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
TESTNET_FUTURES_URL = f"{TESTNET_BASE_URL}/fapi"
TESTNET_FUTURES_DATA_URL = f"{TESTNET_BASE_URL}/futures/data"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

setup_logging()


class MissingCredentialsError(RuntimeError):
    """Raised when the Binance API credentials are not configured."""


@dataclass(frozen=True, slots=True)
class BinanceSettings:
    api_key: str
    api_secret: str


def load_settings() -> BinanceSettings:
    load_dotenv(ENV_FILE)

    api_key = os.getenv("API_KEY", "").strip()
    api_secret = os.getenv("API_SECRET", "").strip()

    if not api_key or not api_secret:
        raise MissingCredentialsError(
            "Missing Binance credentials. Add API_KEY and API_SECRET to the .env file."
        )

    return BinanceSettings(api_key=api_key, api_secret=api_secret)


@lru_cache(maxsize=1)
def get_binance_client() -> Client:
    settings = load_settings()
    client = Client(
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        testnet=True,
        ping=False,
        requests_params={"timeout": 15},
    )

    # Keep the client pinned to Binance USD-M Futures Testnet endpoints.
    if hasattr(client, "FUTURES_URL"):
        client.FUTURES_URL = TESTNET_FUTURES_URL
    if hasattr(client, "FUTURES_DATA_URL"):
        client.FUTURES_DATA_URL = TESTNET_FUTURES_DATA_URL

    return client


def reset_client_cache() -> None:
    get_binance_client.cache_clear()

