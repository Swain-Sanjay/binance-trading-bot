from __future__ import annotations

import logging

import streamlit as st

from bot.client import MissingCredentialsError
from bot.logging_config import setup_logging
from bot.orders import OrderProcessingError, place_order
from bot.validators import InputValidationError

setup_logging()
logger = logging.getLogger("trading_bot.ui")

st.set_page_config(page_title="Binance Futures Testnet Bot", page_icon="📈", layout="centered")

st.title("Binance Futures Testnet Trading Bot")
st.caption("Place USDT-M Futures Testnet orders from a simple Streamlit interface.")

with st.container(border=True):
    col1, col2 = st.columns(2)
    symbol = col1.text_input("Symbol", value="BTCUSDT", help="Example: BTCUSDT").strip()
    side = col2.selectbox("Side", options=["BUY", "SELL"])

    col3, col4 = st.columns(2)
    order_type = col3.selectbox("Order Type", options=["MARKET", "LIMIT"])
    quantity = col4.number_input("Quantity", min_value=0.0, value=0.001, step=0.001, format="%.6f")

    price = None
    if order_type == "LIMIT":
        price = st.number_input("Price", min_value=0.0, value=65000.0, step=10.0, format="%.2f")

    place_order_clicked = st.button("Place Order", type="primary", use_container_width=True)

if place_order_clicked:
    try:
        with st.spinner("Submitting order to Binance Futures Testnet..."):
            response = place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
            )

        st.success(response["message"])
        st.subheader("Order Response")
        st.json(response)
    except InputValidationError as exc:
        logger.warning("UI validation error: %s", exc)
        st.error(str(exc))
    except MissingCredentialsError as exc:
        logger.error("UI credentials error: %s", exc)
        st.error(str(exc))
    except OrderProcessingError as exc:
        logger.error("UI processing error: %s", exc)
        st.error(str(exc))

