from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from bot.client import MissingCredentialsError
from bot.logging_config import setup_logging
from bot.orders import OrderProcessingError, place_order
from bot.validators import InputValidationError

setup_logging()
logger = logging.getLogger("trading_bot.api")

app = FastAPI(
    title="Binance Futures Testnet Trading Bot",
    description="FastAPI backend for placing Binance USD-M Futures Testnet orders.",
    version="1.0.0",
)


class OrderRequestModel(BaseModel):
    symbol: str = Field(..., examples=["BTCUSDT"])
    side: str = Field(..., examples=["BUY"])
    type: str = Field(..., examples=["MARKET"])
    quantity: float = Field(..., gt=0, examples=[0.001])
    price: float | None = Field(default=None, gt=0, examples=[65000])


@app.middleware("http")
async def log_http_traffic(request: Request, call_next):
    body = await request.body()
    body_preview = body.decode("utf-8") if body else ""
    logger.info(
        "Incoming API request: method=%s path=%s body=%s",
        request.method,
        request.url.path,
        body_preview,
    )

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": body, "more_body": False}

    request_with_body = Request(request.scope, receive)

    try:
        response = await call_next(request_with_body)
    except Exception:
        logger.exception("Unhandled FastAPI error for %s %s", request.method, request.url.path)
        raise

    logger.info(
        "Outgoing API response: method=%s path=%s status=%s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/order")
def create_order(order_request: OrderRequestModel) -> dict[str, Any]:
    try:
        response = place_order(
            symbol=order_request.symbol,
            side=order_request.side,
            order_type=order_request.type,
            quantity=order_request.quantity,
            price=order_request.price,
        )
        logger.info("POST /order success: %s", json.dumps(response.get("order", {})))
        return response
    except InputValidationError as exc:
        logger.warning("POST /order validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except MissingCredentialsError as exc:
        logger.error("POST /order credentials error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except OrderProcessingError as exc:
        logger.error("POST /order processing error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

