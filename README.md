# 🐇 RabbitX Python Client

A modern, high-performance Python SDK for interacting with the [RabbitX](https://rabbitx.io) decentralized perpetuals exchange. This package enables seamless trading, account management, market data access, and real-time event handling via both REST and WebSocket APIs.

---

## ✨ Features

- **Simple, unified API** for trading, account, and market operations
- **WebSocket streaming** for real-time orderbook, trades, and account updates
- **Secure authentication** with API key (recommended) or private key (not recommended)
- **Supports multiple networks**: Ethereum, Blast, and other networks as well as their testnets
- **Threaded** and **async** support for the all REST API and WebSocket API
- **Comprehensive examples** for rapid integration

---

## 🚀 Quick Start

### Installation

It's necessary to install [uv](https://docs.astral.sh/uv/) first.

1. Clone the repository

```bash
git clone https://github.com/rabbitx-io/python-rabbitx.git
cd python-rabbitx
```

2. Install dependencies
```bash
uv sync
```

### Run examples

1. Create a `.apikey/apiKey.json` file with your API key. See the [Generate Your API Keys](https://docs.rabbitx.com/api-documentation/generate-your-api-keys) for more information.

2. Run the example:

```bash
uv run examples/auth_api_key.py
```

---

## 🛠️ Usage

Below is a comprehensive example that demonstrates onboarding, real-time market data streaming, and automated order management:

```python
from rabbitx import RabbitX, consts
from rabbitx.apikey import ApiKey
from rabbitx.ws import WS, Orderbook, OpenedOrders, Positions
import time

# Initialize client with API key (recommended)
rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET, api_key=ApiKey.from_file(".apikey/apiKey.json")
)

# Alternative: Initialize with private key (not recommended)
# from rabbitx.wallet import Wallet
# rabbitx = RabbitX(
#     network=consts.ETHEREUM_MAINNET, wallet=Wallet.from_file(".wallets/wallet.pk")
# )
# rabbitx.account.onboarding()  # Required for wallet-based auth

# Get profile information
profile = rabbitx.account.info().result()
print(f"Profile: {profile}")

# Get market information
markets = rabbitx.markets.list().result()
btc_market = rabbitx.markets.info("BTC-USD").result()
print(f"BTC-USD Market Info: {btc_market}")

# Place a limit order
limit_order = rabbitx.orders.create(
    market_id="BTC-USD",
    type="limit",
    side="long",
    price=50000,  # Replace with desired price
    size=0.001,   # Replace with desired size
    time_in_force="good_till_cancel"  # Optional: good_till_cancel, immediate_or_cancel, fill_or_kill, post_only
).result()
print(f"Limit Order Created: {limit_order}")

# Place a market order
market_order = rabbitx.orders.create(
    market_id="BTC-USD",
    type="market",
    side="short",
    size=0.001
).result()
print(f"Market Order Created: {market_order}")

# Place a stop loss order
stop_loss = rabbitx.orders.create(
    market_id="BTC-USD",
    type="stop_loss",
    side="short",
    price=48000,
    size=0.001,
    trigger_price=49000
).result()
print(f"Stop Loss Created: {stop_loss}")

# Get list of orders with filters
active_orders = rabbitx.orders.list(
    market_id="BTC-USD",
    status=["open", "processing"],
    order_type=["limit", "stop_loss"]
).result()
print(f"Active Orders: {active_orders}")

# Amend an order
amended_order = rabbitx.orders.amend(
    market_id="BTC-USD",
    order_id=limit_order["id"],
    price=50500,  # New price
    size=0.002    # New size
).result()
print(f"Amended Order: {amended_order}")

# Cancel specific order
canceled = rabbitx.orders.cancel(
    market_id="BTC-USD",
    order_id=limit_order["id"]
).result()
print(f"Canceled Order: {canceled}")

# Cancel all orders
rabbitx.orders.cancel_all().result()

# WebSocket Integration Example

def handle_orderbook(market_id: str, side: str, price: float, amount: float):
    print(f"Orderbook Update - {market_id} {side}: {price} @ {amount}")

def handle_order_update(order: dict):
    print(f"Order Update: {order}")

def handle_position_update(market_id: str, position: dict):
    print(f"Position Update - {market_id}: {position}")

# Initialize WebSocket handlers
orderbook = Orderbook("BTC-USD", on_update=handle_orderbook)
opened_orders = OpenedOrders(on_update=handle_order_update)
positions = Positions(on_update=handle_position_update)

# Initialize WebSocket connection
token = rabbitx.account.renew_jwt_token().result()["jwt"]
ws = WS(
    token=token,
    network=consts.ETHEREUM_MAINNET,
)

# Register handlers
ws.register_handler("orderbook:BTC-USD", orderbook)
ws.register_handler(f"account@{profile['id']}", opened_orders)
ws.register_handler(f"account@{profile['id']}", positions)

# Start WebSocket connection
ws.start()

# Keep the connection alive for a while
time.sleep(10)

# Get current state
print(f"Best Bid: {orderbook.best_bid()}")
print(f"Best Ask: {orderbook.best_ask()}")
print(f"Open Orders: {opened_orders.get_orders()}")
print(f"Positions: {positions.get_positions()}")

# Stop WebSocket connection
ws.stop()

# Async Support
# The library also supports async operations:
# 
# async with AsyncRabbitX(network=consts.ETHEREUM_MAINNET, api_key=api_key) as rabbitx:
#     markets = await rabbitx.markets.list()
#     order = await rabbitx.orders.create(
#         market_id="BTC-USD",
#         type="limit",
#         side="long",
#         price=50000,
#         size=0.001
#     )
```

---

## 📚 API Overview

### Initialization

```python
from rabbitx import RabbitX, consts
from rabbitx.apikey import ApiKey

rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET,
    api_key=ApiKey.from_file(".apikey/apiKey.json")
)
```

### REST API
- `rabbitx.account` – Account onboarding, profile, balances
- `rabbitx.orders` – Create, amend, cancel, and list orders
- `rabbitx.markets` – Market info, fair price, etc.
- `rabbitx.vaults` – Vault management

### WebSocket API
- `WS` or `AsyncWS` – Real-time connection and channel management
- `Orderbook`, `OpenedOrders`, `Positions` – Real-time data handlers

---

## 🌐 Supported Networks

| Name                | Constant                | Description         |
|---------------------|------------------------|---------------------|
| Ethereum Mainnet    | `ETHEREUM_MAINNET`     | Main production     |
| Ethereum Testnet    | `ETHEREUM_TESTNET`     | Sepolia testnet     |
| Blast Mainnet       | `BLAST_MAINNET`        | Blast production    |
| Blast Testnet       | `BLAST_TESTNET`        | Blast Sepolia test  |
| Arbitrum            | `ARBITRUM`             | Arbitrum mainnet    |
| Base                | `BASE`                 | Base mainnet        |
| Sonic               | `SONIC`                | Sonic mainnet       |

---

## 📦 Examples

See the [`examples/`](examples/) folder for more scripts:
- Account onboarding
- Order management (create, amend, cancel)
- Market data
- WebSocket streaming

---

## 📝 License

MIT

---

## 🤝 Contributing

Pull requests and issues are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 💬 Support

For questions, join the [RabbitX Discord](https://discord.gg/rabbitx) or open an issue on GitHub.
