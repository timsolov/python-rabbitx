.. python-rabbitx documentation master file, created by sphinx-quickstart
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-rabbitx's documentation!
================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   api

Introduction
------------

python-rabbitx is a Python client for interacting with the RabbitX exchange. It provides a high-level API for account management, order handling, market data, and more. Most common API endpoints are demonstrated in the `examples` directory.

**Features:**

- Account onboarding and management
- Secure API key and private key authentication
- Order creation, amendment, and cancellation
- Market data retrieval
- WebSocket support for real-time updates

**Quickstart Example:**

.. code-block:: python

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

   # Get list of fills
   fills = rabbitx.orders.fills(
      market_id="BTC-USD",
   ).result()
   print(f"Fills: {fills}")

   # Get market candles
   candles = rabbitx.markets.candles(
      market_id="BTC-USD",
      start_time=1,
      end_time=int(time.time()),
      period="1h",
   ).result()
   print(f"Candles: {candles}")

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

See the :doc:`usage` section for more detailed examples.

