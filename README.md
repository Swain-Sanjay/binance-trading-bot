# Binance Futures Testnet Trading Bot

A beginner-friendly, production-shaped Python project for placing **Binance USD-M Futures Testnet** orders from:

- a command-line interface
- a FastAPI backend
- a Streamlit user interface

The project uses the Binance Futures Testnet base URL: `https://testnet.binancefuture.com`

## Project Structure

```text
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py
│   ├── logging_config.py
│   ├── orders.py
│   └── validators.py
├── api/
│   └── main.py
├── ui/
│   └── app.py
├── cli.py
├── .env.example
├── requirements.txt
└── README.md
```

## Features

- Connects to Binance USD-M Futures Testnet
- Supports `BUY` and `SELL`
- Supports `MARKET` and `LIMIT` orders
- Validates user inputs before sending requests
- Logs requests, responses, and errors to `bot.log`
- Reuses the same order logic across CLI, API, and UI

## Setup

1. Open a terminal and move into the project folder:

   ```bash
   cd trading_bot
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file:

   ```bash
   copy .env.example .env
   ```

5. Open `.env` and add your Binance Futures Testnet credentials:

   ```env
   API_KEY=your_testnet_api_key
   API_SECRET=your_testnet_api_secret
   ```

## Run the CLI

Example MARKET order:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Example LIMIT order:

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

CLI output includes:

- order summary
- API response fields such as `orderId`, `status`, `executedQty`, and `avgPrice`
- a clear success or failure message

## Run the API

Start the FastAPI server:

```bash
uvicorn api.main:app --reload
```

Create an order:

```bash
curl -X POST "http://127.0.0.1:8000/order" ^
  -H "Content-Type: application/json" ^
  -d "{\"symbol\":\"BTCUSDT\",\"side\":\"BUY\",\"type\":\"MARKET\",\"quantity\":0.001}"
```

Example LIMIT request:

```json
{
  "symbol": "BTCUSDT",
  "side": "SELL",
  "type": "LIMIT",
  "quantity": 0.001,
  "price": 70000
}
```

## Run the UI

Start Streamlit:

```bash
streamlit run ui/app.py
```

The UI lets you:

- enter the symbol
- choose side and order type
- enter quantity
- enter price for LIMIT orders
- submit the order and inspect the JSON response

## Logging

All important application events are written to:

```text
bot.log
```

This includes:

- incoming API requests
- outgoing API responses
- Binance order requests
- Binance responses
- validation, network, and API errors

## Notes

- This project is for **Binance Futures Testnet only**
- Use Testnet API keys, not live account keys
- LIMIT orders automatically use `GTC` time-in-force
- The app validates inputs before the request is sent to Binance

