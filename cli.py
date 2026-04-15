from __future__ import annotations

import argparse
import json
import logging
import sys

from bot.client import MissingCredentialsError
from bot.logging_config import setup_logging
from bot.orders import OrderProcessingError, place_order
from bot.validators import InputValidationError

setup_logging()
logger = logging.getLogger("trading_bot.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place an order on Binance USD-M Futures Testnet."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol, for example BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", required=True, dest="order_type", help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Price for LIMIT orders. Leave empty for MARKET orders.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        response = place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )

        order = response["order"]
        summary = response["submitted_order"]

        print("Order Summary")
        print(json.dumps(summary, indent=2))
        print()
        print("API Response")
        print(
            json.dumps(
                {
                    "orderId": order.get("orderId"),
                    "status": order.get("status"),
                    "executedQty": order.get("executedQty"),
                    "avgPrice": order.get("avgPrice"),
                },
                indent=2,
            )
        )
        print()
        print("Success: Order placed successfully.")
        return 0
    except (InputValidationError, MissingCredentialsError, OrderProcessingError) as exc:
        logger.error("CLI order failed: %s", exc)
        print(f"Failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

