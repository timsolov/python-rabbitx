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
   from rabbitx.apikey import read_from_json_file

   rabbitx = RabbitX(network=consts.ETHEREUM_MAINNET, api_key=read_from_json_file('.apikey/apiKey.json'))
   token = rabbitx.account.renew_jwt_token()['jwt']

   print(f"Token: {token}")

See the :doc:`usage` section for more detailed examples.

