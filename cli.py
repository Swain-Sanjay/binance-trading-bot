"""Command-line interface for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from bot.client import BinanceClientError, create_futures_client
from bot.logging_config import setup_logging
from bot.orders import OrderPlacementError, place_limit_order, place_market_order
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Place MARKET and LIMIT orders on Binance Futures Testnet.",
    )
    parser.add_argument("--symbol", required=True, help="USDT-M futures symbol, for example BTCUSDT.")
    parser.add_argument("--side", required=True, help="Order side: BUY or SELL.")
    parser.add_argument("--type", required=True, help="Order type: MARKET or LIMIT.")
    parser.add_argument("--quantity", required=True, help="Order quantity.")
    parser.add_argument("--price", required=False, help="Order price. Required for LIMIT orders.")
    return parser


def main() -> int:
    """Run the CLI application."""
    logger = setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    try:
        order_request = _validate_args(args)
        _print_section("Order Request Summary", order_request)

        client = create_futures_client()
        if order_request["type"] == "MARKET":
            response = place_market_order(
                client=client,
                symbol=order_request["symbol"],
                side=order_request["side"],
                quantity=order_request["quantity"],
            )
        else:
            response = place_limit_order(
                client=client,
                symbol=order_request["symbol"],
                side=order_request["side"],
                quantity=order_request["quantity"],
                price=order_request["price"],
            )

        _print_section("Order Response", response)
        print("\nSUCCESS: Order request completed.")
        logger.info("CLI order flow completed successfully.")
        return 0
    except (ValueError, BinanceClientError, OrderPlacementError) as exc:
        logger.error("CLI order flow failed: %s", exc)
        print(f"\nFAILURE: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        logger.warning("CLI order flow interrupted by user.")
        print("\nFAILURE: Operation interrupted by user.", file=sys.stderr)
        return 130
    except Exception as exc:
        logger.exception("Unhandled CLI error.")
        print(f"\nFAILURE: Unexpected error: {exc}", file=sys.stderr)
        return 1


def _validate_args(args: argparse.Namespace) -> dict[str, Any]:
    """Validate parsed CLI arguments and return a clean order request."""
    order_type = validate_order_type(args.type)
    return {
        "symbol": validate_symbol(args.symbol),
        "side": validate_side(args.side),
        "type": order_type,
        "quantity": validate_quantity(args.quantity),
        "price": validate_price(args.price, order_type),
    }


def _print_section(title: str, payload: dict[str, Any]) -> None:
    """Print a formatted JSON section to stdout."""
    print(f"\n{title}")
    print("-" * len(title))
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    raise SystemExit(main())

