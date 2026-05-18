"""Binance Futures Testnet client factory."""

from __future__ import annotations

import os
import time

import streamlit as st
from binance.client import Client

from bot.logging_config import setup_logging


TESTNET_FUTURES_BASE_URL = "https://testnet.binancefuture.com"
TESTNET_FUTURES_API_URL = f"{TESTNET_FUTURES_BASE_URL}/fapi"


class BinanceClientError(RuntimeError):
    """Raised when the Binance client cannot be initialized."""


def create_futures_client() -> Client:
    """Create a python-binance client configured for USDT-M Futures Testnet."""

    logger = setup_logging()

    api_key = st.secrets["BINANCE_API_KEY"]
    api_secret = st.secrets["BINANCE_API_SECRET"]

    if not api_key or not api_secret:
        message = "Missing BINANCE_API_KEY or BINANCE_API_SECRET."
        logger.error(message)
        raise BinanceClientError(message)

    try:
        client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True
        )

        # Configure Futures Testnet URL
        client.FUTURES_URL = TESTNET_FUTURES_API_URL

        # Sync timestamp with Binance server
        server_time = client.futures_time()

        client.timestamp_offset = (
            server_time["serverTime"] - int(time.time() * 1000)
        )

        logger.info("Initialized Binance Futures Testnet client.")

        return client

    except Exception as exc:
        logger.exception("Failed to initialize Binance Futures Testnet client.")

        raise BinanceClientError(
            "Unable to initialize Binance Futures client."
        ) from exc


def get_client() -> Client:
    """Return configured Binance Futures client."""
    return create_futures_client()