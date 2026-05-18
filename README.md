# Binance Futures Testnet Trading Bot (USDT-M)

A production-style Python CLI application for placing `MARKET` and `LIMIT` orders on Binance USDT-M Futures Testnet using `python-binance`.

## Features

- Binance Futures Testnet support
- `BUY` and `SELL` sides
- `MARKET` and `LIMIT` orders
- CLI input with `argparse`
- Input validation before API calls
- Structured rotating file logs in `logs/bot.log`
- Environment-based API credentials
- Reusable package architecture
- Clear success and failure output

## Project Structure

```text
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py
│   ├── orders.py
│   ├── validators.py
│   └── logging_config.py
├── logs/
│   └── bot.log
├── cli.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

From this repository root:

```bash
cd trading_bot
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## API Keys

Create a `.env` file from the example:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your Binance Futures Testnet credentials:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

Use API keys from Binance Futures Testnet:

```text
https://testnet.binancefuture.com
```

## Usage

Run commands from inside the `trading_bot` directory.

Market buy example:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Market sell example:

```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

Limit buy example:

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000
```

Limit sell example:

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 90000
```

## Sample Output

```json
Order Request Summary
---------------------
{
  "price": "60000",
  "quantity": "0.001",
  "side": "BUY",
  "symbol": "BTCUSDT",
  "type": "LIMIT"
}

Order Response
--------------
{
  "clientOrderId": "test-order-id",
  "executedQty": "0",
  "orderId": 123456789,
  "origQty": "0.001",
  "price": "60000",
  "side": "BUY",
  "status": "NEW",
  "symbol": "BTCUSDT",
  "timeInForce": "GTC",
  "type": "LIMIT",
  "updateTime": 1710000000000
}

SUCCESS: Order request completed.
```

## Validation Rules

- `--symbol` must be alphanumeric and end with `USDT`
- `--side` must be `BUY` or `SELL`
- `--type` must be `MARKET` or `LIMIT`
- `--quantity` must be greater than zero
- `--price` is required for `LIMIT` orders
- `--price` must not be provided for `MARKET` orders

## Logs

The bot writes API requests, responses, and errors to:

```text
logs/bot.log
```

Logs rotate automatically when the file reaches about 1 MB, keeping five backups.

