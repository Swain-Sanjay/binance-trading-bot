from __future__ import annotations

import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class InputValidationError(ValueError):
    """Raised when the user provides invalid order input."""


def validate_symbol(symbol: str) -> str:
    if not isinstance(symbol, str) or not symbol.strip():
        raise InputValidationError("Symbol is required.")

    normalized_symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(normalized_symbol):
        raise InputValidationError(
            "Symbol must contain only uppercase letters and numbers, for example BTCUSDT."
        )

    if not normalized_symbol.endswith("USDT"):
        raise InputValidationError(
            "Only USDT-M Futures symbols are supported. Example: BTCUSDT."
        )

    return normalized_symbol


def validate_side(side: str) -> str:
    if not isinstance(side, str) or not side.strip():
        raise InputValidationError("Side is required and must be BUY or SELL.")

    normalized_side = side.strip().upper()
    if normalized_side not in VALID_SIDES:
        raise InputValidationError("Side must be either BUY or SELL.")

    return normalized_side


def validate_order_type(order_type: str) -> str:
    if not isinstance(order_type, str) or not order_type.strip():
        raise InputValidationError("Order type is required and must be MARKET or LIMIT.")

    normalized_type = order_type.strip().upper()
    if normalized_type not in VALID_ORDER_TYPES:
        raise InputValidationError("Order type must be either MARKET or LIMIT.")

    return normalized_type


def validate_positive_number(value: float | int | str, field_name: str) -> float:
    try:
        normalized_value = float(value)
    except (TypeError, ValueError) as exc:
        raise InputValidationError(f"{field_name} must be a valid number.") from exc

    if normalized_value <= 0:
        raise InputValidationError(f"{field_name} must be greater than 0.")

    return normalized_value


def validate_price_for_order_type(order_type: str, price: float | int | str | None) -> float | None:
    if order_type == "LIMIT":
        if price is None or price == "":
            raise InputValidationError("Price is required for LIMIT orders.")
        return validate_positive_number(price, "Price")

    return None

