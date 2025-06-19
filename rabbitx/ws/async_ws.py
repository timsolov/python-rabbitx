from .channel_handler import AsyncChannelHandler
from rabbitx.xutils import dict_get_path, dict_has_path
from rabbitx import consts
from typing import Callable
from websockets.exceptions import ConnectionClosedOK
from websockets.asyncio.client import connect
import json
import logging
import os
import ssl
import asyncio

DEBUG = os.getenv("DEBUG", False)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("rabbitx.async_ws")


class AsyncWS:
    """
    AsyncWS class.

    This class is an asynchronous wrapper around the RabbitX WebSocket API.
    """

    def __init__(
        self,
        token: str,
        network: str = None,
        url: str = None,
        channels: list[str] = [],
        on_message: Callable[[str, dict], asyncio.Future] = None,
        on_subscribe: Callable[[str, dict], asyncio.Future] = None,
        ssl_skip_verify: bool = False,
        **kwargs,
    ):
        """
        Initialize the WebSocket connection (async version)

        :param url: The URL of the WebSocket server
        :type url: str
        :param token: The token for the WebSocket connection
        :type token: str
        :param channels: The channels to subscribe to immediately after authorization (it runs subscribe method for each channel).
        :type channels: list[str]
        :param on_message: The async callback function for incoming messages. Should accept two arguments: channel and data (eg. async def on_message(channel, data))
        :type on_message: Callable[[str, dict], asyncio.Future]
        :param on_subscribe: The async callback function for incoming subscribe messages. Should accept two arguments: channel and data (eg. async def on_subscribe(channel, data))
        :type on_subscribe: Callable[[str, dict], asyncio.Future]
        :param ssl_skip_verify: Whether to skip SSL verification
        :type ssl_skip_verify: bool
        :param kwargs: Additional keyword arguments which will be passed to the websockets.async.client.connect function
        """
        if not url and not network:
            raise Exception("Either url or network must be provided")

        if url and network:
            raise Exception("Both url and network cannot be provided")

        if network and network not in consts.WS_URL:
            raise ValueError(f"Invalid network: {network}")

        self.url = url or consts.WS_URL[network]
        self.conn = None
        self.on_message = on_message
        self.on_subscribe = on_subscribe
        self.token = token
        self.message_id = 0
        self.promises = {}
        self.channels = channels
        self.subscribed = {}
        self.authorized = False
        self.connected = False
        self.handlers = {}
        self.connection_params = kwargs
        if ssl_skip_verify:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            self.connection_params.update({"ssl": ssl_context})
        self._websocket_task = None
        self._stop_event = asyncio.Event()

    def register_handler(self, channel: str, handler: AsyncChannelHandler):
        """
        Register a handler for a channel.

        The handler should be registered before subscribing to the channel.
        Otherwise, you're in risk of missing messages.
        The handler will be called with the data of the subscription.
        The handler will be called with the data of the message.

        Example:

        .. code-block:: python

            from rabbitx.ws.async_ws import AsyncWS
            from rabbitx.ws.channel_handler import AsyncChannelHandler

            class OrderbookHandler(AsyncChannelHandler):
                async def on_subscribe(self, data):
                    print(f"[ORDERBOOK] Subscribed: {data}")
                    await setup_async(data)

                async def on_data(self, data):
                    print(f"[ORDERBOOK] Data: {data}")
                    await create_order(data)

            channel = "orderbook:BTC-USD"
            ws = AsyncWS(...)
            ws.register_handler(channel, OrderbookHandler(channel))

            await ws.start()

        :param channel: The channel to register the handler for
        :type channel: str
        :param handler: The handler to register
        :type handler: AsyncChannelHandler
        """
        if channel not in self.handlers:
            self.handlers[channel] = []
        self.handlers[channel].append(handler)

        if not self.connected:
            if channel not in self.channels:
                self.channels.append(channel)

    async def _connect(self):
        """
        Connect to the WebSocket server.
        """
        try:
            self.conn = await connect(self.url, **self.connection_params)
            if DEBUG:
                logger.debug("Connected to %s", self.url)
            self.connected = True
            if self.token:
                await self._authorize()
        except Exception as e:
            logger.error("Error in connect(): %s", e)
            raise

    async def _disconnect(self):
        """
        Disconnect from the WebSocket server.
        """
        if self.conn:
            await self.conn.close()
            self.conn = None

        self.authorized = False
        self.connected = False

    async def send(self, message: str):
        """
        Send a message to the WebSocket server.

        :param message: The raw message to send (json string)
        :type message: str
        """
        await self.conn.send(message)

    async def request(self, message: dict, callback: Callable[[dict], asyncio.Future]):
        """
        Send a message to the WebSocket server with a callback function
        which will be called when the message is received.
        The callback function will be called with the received message as an argument.

        :param message: The message to send (json object)
        :type message: dict
        :param callback: The callback function to call when the message is received (eg. async callback(message))
        :type callback: Callable[[dict], asyncio.Future]
        """
        self.message_id += 1
        self.promises[self.message_id] = callback
        message.update({"id": self.message_id})
        await self.send(json.dumps(message))

    async def _authorize(self):
        """
        Authorize the WebSocket connection.
        This method will send the authorize message to the WebSocket server
        and subscribe to the channels specified in the constructor.

        It's not necessary to call this method manually.
        It's called automatically when the connection is established.
        """

        async def on_authorized(_):
            if DEBUG:
                logger.debug("Authorized")
            self.authorized = True
            for channel in self.channels:
                await self.subscribe(channel)

        await self.request(
            {"connect": {"token": self.token, "name": "js"}}, on_authorized
        )

    async def subscribe(self, channel: str):
        """
        Subscribe to a channel.

        There are two ways to handle messages from subscribed channels:
        1. Define the on_subscribe and on_message callbacks in the constructor.

            Example:

            .. code-block:: python

                from rabbitx.ws import AsyncWS

                async def on_message(channel, data):
                    print(f"[MESSAGE] Channel: {channel}, Data: {data}")
                    await process_data_async(data)

                async def on_subscribe(channel, data):
                    print(f"[SUBSCRIBED] Channel: {channel}, Data: {data}")
                    await setup_async(data)

                ws = AsyncWS(
                    token=token,
                    on_subscribe=on_subscribe,
                    on_message=on_message,
                )

                await ws.start()

        2. Register a handler for a channel using the register_handler method.

            Example:

            .. code-block:: python

                from rabbitx.ws.channel_handler import AsyncChannelHandler
                from rabbitx.ws import AsyncWS

                class OrderbookHandler(AsyncChannelHandler):
                    async def on_subscribe(self, data):
                        print(f"[ORDERBOOK] Subscribed: {data}")
                        await setup_async(data)

                    async def on_data(self, data):
                        print(f"[ORDERBOOK] Data: {data}")
                        await create_order(data)

                channel = "orderbook:BTC-USD"
                ws = AsyncWS(...)
                ws.register_handler(channel, OrderbookHandler(channel))

                await ws.start()

        :param channel: The channel to subscribe to
        :type channel: str
        """

        if not self.connected and channel not in self.channels:
            self.channels.append(channel)
            return
        
        async def on_subscribe(msg):
            if DEBUG:
                logger.debug("Subscribed to %s", channel)
            self.subscribed[channel] = True
            data = msg["subscribe"]["data"]
            await self._handle_subscribe(channel, data)

        await self.request(
            {
                "subscribe": {"channel": channel},
            },
            on_subscribe,
        )

    async def _handle_message(self, channel: str, data: dict):
        """Handle an incoming message from a channel"""
        if DEBUG:
            logger.debug(f"handle_message {channel} {data}")
        if self.on_message:
            try:
                await self.on_message(channel, data)
            except Exception as e:
                logger.error(f"Error in on_message callback: {e}")
        if channel in self.handlers:
            for handler in self.handlers[channel]:
                try:
                    await handler.on_data(data)
                except Exception as e:
                    logger.error(
                        f"Error in handler {handler.__class__.__name__}.on_data: {e}"
                    )

    async def _handle_subscribe(self, channel: str, data: dict):
        """Handle a subscription confirmation"""
        if DEBUG:
            logger.debug(f"handle_subscribe {channel} {data}")
        if self.on_subscribe:
            try:
                await self.on_subscribe(channel, data)
            except Exception as e:
                logger.error(f"Error in on_subscribe callback: {e}")
        if channel in self.handlers:
            for handler in self.handlers[channel]:
                try:
                    await handler.on_subscribe(data)
                except Exception as e:
                    logger.error(
                        f"Error in handler {handler.__class__.__name__}.on_subscribe: {e}"
                    )

    async def _process_message(self, message: str):
        """
        Process a message received from the WebSocket server.

        :param message: The raw message received from the WebSocket server (json string)
        :type message: str
        """
        msg = json.loads(message)

        if dict_has_path(msg, "id") and msg["id"] in self.promises:
            callback = self.promises[msg["id"]]
            del self.promises[msg["id"]]
            await callback(msg)
            return

        if dict_has_path(msg, "channel"):
            channel = dict_get_path(msg, "channel")
            if dict_has_path(msg, "data"):
                data = dict_get_path(msg, "data")
                await self._handle_message(channel, data)
            elif dict_has_path(msg, "subscribe"):
                data = dict_get_path(msg, "subscribe")
                await self._handle_subscribe(channel, data)

    async def _run(self):
        try:
            logger.debug("Attempting to connect to WebSocket...")
            await self._connect()
            logger.debug("WebSocket connected successfully")

            while not self._stop_event.is_set():
                try:
                    message = await asyncio.wait_for(self.conn.recv(), timeout=1)
                except asyncio.TimeoutError:
                    continue
                except ConnectionClosedOK as e:
                    logger.error("Connection closed: %s", e)
                    break

                if DEBUG:
                    logger.debug("Received message: %s", message)

                if message == "{}":
                    await self.send("{}")
                    continue

                if "\n" in message:
                    for msg in message.split("\n"):
                        if msg.strip() == "":
                            continue
                        await self._process_message(msg)
                else:
                    await self._process_message(message)

        except Exception as e:
            logger.error("Error in WebSocket: %s", e)
        finally:
            await self._disconnect()

    async def start(self):
        """Create a task for the WebSocket connection"""
        self._websocket_task = asyncio.create_task(self._run())
        return self._websocket_task

    async def stop(self):
        """Cancel the WebSocket connection task"""
        self._stop_event.set()
        if self.conn:
            try:
                await self._disconnect()
            except Exception:
                pass
        if self._websocket_task:
            self._websocket_task.cancel()
            self._websocket_task = None
