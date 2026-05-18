"""Input validation helpers for order requests."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    """Validate and normalize a Binance Futures symbol."""
    normalized = (symbol or "").strip().upper()

    if not normalized:
        raise ValueError("Symbol is required.")
    if not normalized.isalnum():
        raise ValueError("Symbol must contain only letters and numbers.")
    if not normalized.endswith("USDT"):
        raise ValueError("This bot is intended for USDT-M futures symbols ending in USDT.")

    return normalized


def validate_side(side: str) -> str:
    """Validate and normalize order side."""
    normalized = (side or "").strip().upper()

    if normalized not in VALID_SIDES:
        raise ValueError(f"Side must be one of: {', '.join(sorted(VALID_SIDES))}.")

    return normalized


def validate_order_type(order_type: str) -> str:
    """Validate and normalize order type."""
    normalized = (order_type or "").strip().upper()

    if normalized not in VALID_ORDER_TYPES:
        raise ValueError(f"Type must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}.")

    return normalized


def validate_quantity(quantity: str | float | int) -> str:
    """Validate order quantity and return it as a Binance-compatible string."""
    decimal_quantity = _positive_decimal(quantity, "Quantity")
    return _format_decimal(decimal_quantity)


def validate_price(price: str | float | int | None, order_type: str) -> str | None:
    """Validate price rules for market and limit orders."""
    normalized_type = validate_order_type(order_type)

    if normalized_type == "MARKET":
        if price not in (None, ""):
            raise ValueError("Price must not be provided for MARKET orders.")
        return None

    if price in (None, ""):
        raise ValueError("Price is required for LIMIT orders.")

    decimal_price = _positive_decimal(price, "Price")
    return _format_decimal(decimal_price)


def _positive_decimal(value: str | float | int, field_name: str) -> Decimal:
    """Parse a positive decimal value from CLI input."""
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc

    if decimal_value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return decimal_value


def _format_decimal(value: Decimal) -> str:
    """Return a plain decimal string without scientific notation."""
    return format(value.normalize(), "f")

