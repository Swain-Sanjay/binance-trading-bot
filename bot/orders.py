from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import requests
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import MissingCredentialsError, get_binance_client
from bot.logging_config import setup_logging
from bot.validators import (
    InputValidationError,
    validate_order_type,
    validate_positive_number,
    validate_price_for_order_type,
    validate_side,
    validate_symbol,
)

setup_logging()
logger = logging.getLogger("trading_bot.orders")


class OrderProcessingError(RuntimeError):
    """Raised when an order cannot be sent or finalized."""


@dataclass(frozen=True, slots=True)
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None

    @classmethod
    def from_payload(
        cls,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float | int | str,
        price: float | int | str | None = None,
    ) -> "OrderRequest":
        normalized_order_type = validate_order_type(order_type)
        return cls(
            symbol=validate_symbol(symbol),
            side=validate_side(side),
            order_type=normalized_order_type,
            quantity=validate_positive_number(quantity, "Quantity"),
            price=validate_price_for_order_type(normalized_order_type, price),
        )

    def to_exchange_params(self) -> dict[str, str]:
        params: dict[str, str] = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": format_decimal(self.quantity),
        }

        if self.order_type == "LIMIT":
            params["price"] = format_decimal(self.price)
            params["timeInForce"] = "GTC"

        return params

    def to_summary(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
            "price": self.price,
        }


def format_decimal(value: float | None) -> str:
    if value is None:
        return ""

    formatted = f"{value:.12f}".rstrip("0").rstrip(".")
    return formatted if formatted else "0"


def _format_binance_error(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    message = getattr(exc, "message", None)
    status_code = getattr(exc, "status_code", None)

    if code is not None and message:
        return f"Binance API error {code}: {message}"
    if status_code is not None and message:
        return f"Binance API error {status_code}: {message}"
    return str(exc)


def _fetch_order_status(client: Any, request: OrderRequest, order_id: int | None) -> dict[str, Any]:
    if order_id is None:
        return {}

    try:
        status_response = client.futures_get_order(symbol=request.symbol, orderId=order_id)
        logger.info("Binance futures_get_order response: %s", status_response)
        return status_response
    except (BinanceAPIException, BinanceRequestException, requests.RequestException) as exc:
        logger.warning("Could not fetch final order status for orderId=%s: %s", order_id, exc)
        return {}


def _build_order_payload(
    request: OrderRequest,
    create_response: dict[str, Any],
    status_response: dict[str, Any],
) -> dict[str, Any]:
    merged = {**create_response, **status_response}
    return {
        "orderId": merged.get("orderId"),
        "symbol": merged.get("symbol", request.symbol),
        "side": merged.get("side", request.side),
        "type": merged.get("type", request.order_type),
        "status": merged.get("status", "UNKNOWN"),
        "price": merged.get("price", format_decimal(request.price) if request.price else "0"),
        "origQty": merged.get("origQty", format_decimal(request.quantity)),
        "executedQty": merged.get("executedQty", "0"),
        "avgPrice": merged.get("avgPrice", "0"),
        "clientOrderId": merged.get("clientOrderId"),
        "updateTime": merged.get("updateTime"),
    }


def place_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float | int | str,
    price: float | int | str | None = None,
) -> dict[str, Any]:
    try:
        request = OrderRequest.from_payload(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )
        payload = request.to_exchange_params()
        logger.info("Preparing Binance Futures Testnet order: %s", request.to_summary())
        logger.info("Binance futures_create_order payload: %s", payload)

        client = get_binance_client()
        create_response = client.futures_create_order(**payload)
        logger.info("Binance futures_create_order response: %s", create_response)

        order_id = create_response.get("orderId")
        status_response = _fetch_order_status(client, request, order_id)
        order_payload = _build_order_payload(request, create_response, status_response)

        return {
            "message": "Order placed successfully.",
            "submitted_order": request.to_summary(),
            "order": order_payload,
            "raw": {
                "create_response": create_response,
                "order_status": status_response,
            },
        }
    except InputValidationError:
        logger.exception("Input validation failed while placing an order.")
        raise
    except MissingCredentialsError:
        logger.exception("Binance credentials are missing.")
        raise
    except BinanceAPIException as exc:
        logger.exception("Binance API rejected the order.")
        raise OrderProcessingError(_format_binance_error(exc)) from exc
    except BinanceRequestException as exc:
        logger.exception("Binance request failed before a valid response was returned.")
        raise OrderProcessingError(f"Binance request failed: {exc}") from exc
    except requests.RequestException as exc:
        logger.exception("Network failure while talking to Binance.")
        raise OrderProcessingError(f"Network failure while talking to Binance: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error while placing an order.")
        raise OrderProcessingError(f"Unexpected error while placing the order: {exc}") from exc
