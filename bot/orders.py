"""Order placement service functions."""

from __future__ import annotations

from typing import Any

from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

from bot.logging_config import setup_logging


TIME_IN_FORCE_GTC = "GTC"


class OrderPlacementError(RuntimeError):
    """Raised when an order cannot be placed."""


def place_market_order(client: Any, symbol: str, side: str, quantity: str) -> dict[str, Any]:
    """Place a Binance Futures market order and return a clean response."""
    request_payload = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
    }
    return _place_order(client, request_payload)


def place_limit_order(
    client: Any,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
) -> dict[str, Any]:
    """Place a Binance Futures limit order and return a clean response."""
    request_payload = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "timeInForce": TIME_IN_FORCE_GTC,
        "quantity": quantity,
        "price": price,
    }
    return _place_order(client, request_payload)


def format_order_response(response: dict[str, Any]) -> dict[str, Any]:
    """Extract the most useful fields from the Binance order response."""
    fields = (
        "orderId",
        "symbol",
        "status",
        "clientOrderId",
        "price",
        "avgPrice",
        "origQty",
        "executedQty",
        "cumQty",
        "cumQuote",
        "type",
        "side",
        "timeInForce",
        "updateTime",
    )
    return {field: response.get(field) for field in fields if field in response}


def _place_order(client: Any, request_payload: dict[str, Any]) -> dict[str, Any]:
    """Send an order request to Binance and handle API errors consistently."""
    logger = setup_logging()
    logger.info("Order request: %s", request_payload)

    try:
        response = client.futures_create_order(**request_payload)
        formatted_response = format_order_response(response)
        logger.info("Order response: %s", formatted_response)
        return formatted_response
    except (BinanceAPIException, BinanceOrderException, BinanceRequestException) as exc:
        logger.exception("Binance order request failed: %s", exc)
        raise OrderPlacementError(f"Binance rejected the order: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected order placement error.")
        raise OrderPlacementError("Unexpected error while placing the order.") from exc

