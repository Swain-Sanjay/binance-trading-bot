"""Binance Futures Testnet client factory."""

from __future__ import annotations

import time

import streamlit as st
from binance.client import Client

from bot.logging_config import setup_logging


TESTNET_FUTURES_URL = "https://testnet.binancefuture.com/fapi"


class BinanceClientError(RuntimeError):
    """Raised when the Binance client cannot be initialized."""


def create_futures_client() -> Client:
    """Create Binance Futures Testnet client."""

    logger = setup_logging()

    try:
        api_key = st.secrets["BINANCE_API_KEY"]
        api_secret = st.secrets["BINANCE_API_SECRET"]

    except Exception:
        raise BinanceClientError(
            "Missing BINANCE_API_KEY or BINANCE_API_SECRET in Streamlit secrets."
        )

    try:
        client = Client(
            api_key,
            api_secret,
            testnet=True
        )

        # Set Futures Testnet URL
        client.FUTURES_URL = TESTNET_FUTURES_URL

        # Sync server time
        server_time = client.futures_time()

        client.timestamp_offset = (
            server_time["serverTime"] - int(time.time() * 1000)
        )

        # Test connection
        client.futures_ping()

        logger.info("Initialized Binance Futures Testnet client.")

        return client

    except Exception as exc:
        logger.exception("Failed to initialize Binance Futures client.")

        raise BinanceClientError(
            f"Unable to initialize Binance Futures client: {exc}"
        ) from exc


def get_client() -> Client:
    """Return configured Binance Futures client."""
    return create_futures_client()