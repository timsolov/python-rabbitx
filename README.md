# 🐇 RabbitX Python Client

A modern, high-performance Python SDK for interacting with the [RabbitX](https://rabbitx.io) decentralized perpetuals exchange. This package enables seamless trading, account management, market data access, and real-time event handling via both REST and WebSocket APIs.

---

## ✨ Features

- **Simple, unified API** for trading, account, and market operations
- **WebSocket streaming** for real-time orderbook, trades, and account updates
- **Secure authentication** with private key or API key
- **Supports multiple networks**: Ethereum, Blast, and their testnets
- **Comprehensive examples** for rapid integration

---

## 🚀 Quick Start

### Installation

```bash
uv sync
```

### Run examples

```bash
uv run examples/auth_api_key.py
```

---

## 🛠️ Usage

Below is a comprehensive example that demonstrates onboarding, real-time market data streaming, and automated order management:

```python
from rabbitx import RabbitX, consts
from rabbitx.apikey import read_from_json_file

rabbitx = RabbitX(network=consts.ETHEREUM_MAINNET, api_key=read_from_json_file('.apikey/apiKey.json'))

# Replace with real values as needed
order = rabbitx.orders.create(
    market_id="BTC-USD",
    type="limit",
    side="long",
    price=10000,
    size=0.001
)

print(f"Order created: {order}") 
```

---

## 📚 API Overview

### Initialization

```python
from rabbitx import RabbitX, consts
rabbitx = RabbitX(
    network=consts.ETHEREUM_MAINNET,
    wallet_pk="<your_private_key>"    # or use api_key="<your_api_key>"
)
```

### REST API
- `rabbitx.account` – Account onboarding, profile, balances
- `rabbitx.orders` – Create, amend, cancel, and list orders
- `rabbitx.markets` – Market info, fair price, etc.
- `rabbitx.vaults` – Vault management

### WebSocket API
- `WS` – Real-time connection and channel management
- `Orderbook`, `OpenedOrders`, `Positions` – Real-time data handlers

---

## 🌐 Supported Networks

| Name                | Constant                | Description         |
|---------------------|------------------------|---------------------|
| Ethereum Mainnet    | `ETHEREUM_MAINNET`     | Main production     |
| Ethereum Testnet    | `ETHEREUM_TESTNET`     | Sepolia testnet     |
| Blast Mainnet       | `BLAST_MAINNET`        | Blast production    |
| Blast Testnet       | `BLAST_TESTNET`        | Blast Sepolia test  |

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
