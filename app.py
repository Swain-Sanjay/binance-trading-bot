import streamlit as st
from bot.orders import place_market_order, place_limit_order
from bot.logging_config import setup_logging
from bot.client import get_client

# Setup logging
logger = setup_logging()

# Initialize Binance client
client = get_client()

# Streamlit page settings
st.set_page_config(
    page_title="Binance Futures Testnet Bot",
    page_icon="📈",
    layout="centered"
)

# UI Header
st.title("📈 Binance Futures Testnet Trading Bot")
st.markdown("Place MARKET and LIMIT orders on Binance Futures Testnet")

# Input fields
symbol = st.text_input("Trading Symbol", value="BTCUSDT")

side = st.selectbox(
    "Order Side",
    ["BUY", "SELL"]
)

order_type = st.selectbox(
    "Order Type",
    ["MARKET", "LIMIT"]
)

quantity = st.number_input(
    "Quantity",
    min_value=0.001,
    value=0.001,
    step=0.001,
    format="%.3f"
)

price = None

# Show price field only for LIMIT orders
if order_type == "LIMIT":
    price = st.number_input(
        "Limit Price",
        min_value=1.0,
        value=60000.0,
        step=1.0
    )

# Place order button
if st.button("Place Order"):
    try:
        st.info("Submitting order to Binance Futures Testnet...")

        # MARKET order
        if order_type == "MARKET":
            response = place_market_order(
                client=client,
                symbol=symbol,
                side=side,
                quantity=quantity
            )

        # LIMIT order
        else:
            response = place_limit_order(
                client=client,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price
            )

        st.success("✅ Order placed successfully")

        st.subheader("Order Response")
        st.json(response)

        logger.info("UI order submitted successfully")

    except Exception as exc:
        logger.exception("UI order failed")
        st.error(f"❌ Order failed: {exc}")