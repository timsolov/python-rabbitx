from .channel_handler import ChannelHandler
from rabbitx.xutils import dict_get_path, dict_has_path
from typing import Callable
from websockets.exceptions import ConnectionClosedOK
from websockets.sync.client import connect
import json
import logging
import os
import ssl
import threading
import queue
from rabbitx import consts

DEBUG = os.getenv("DEBUG", False)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("rabbitx.ws")


class WS:
    """
    WS class.

    This class is a wrapper around the RabbitX WebSocket API.

    Attributes
    ----------
    token: str
        The token for the WebSocket connection
    network: str
        The network to connect to (e.g. consts.ETHEREUM_MAINNET)
    url: str
        The URL of the WebSocket server (e.g. consts.WS_URL[network] or custom URL) or None if network is provided
    channels: list[str]
        The channels to subscribe to immediately after authorization (it runs subscribe method for each channel).
    on_message: Callable[[str, dict], None]
        The callback function for incoming messages it should accept two arguments: channel and data (eg. on_message(channel, data)).
    on_subscribe: Callable[[str, dict], None]
        The callback function for incoming subscribe messages it should accept two arguments: channel and data (eg. on_subscribe(channel, data)).

    """

    def __init__(
        self,
        token: str,
        network: str = None,
        url: str = None,
        channels: list[str] = [],
        on_message: Callable[[str, dict], None] = None,
        on_subscribe: Callable[[str, dict], None] = None,
        ssl_skip_verify: bool = False,
        **kwargs,
    ):
        """
        Initialize the WebSocket connection (sync version)

        :param url: The URL of the WebSocket server
        :type url: str
        :param token: The token for the WebSocket connection
        :type token: str
        :param channels: The channels to subscribe to immediately after authorization (it runs subscribe method for each channel).
        :type channels: list[str]
        :param on_message: The callback function for incoming messages it should accept two arguments: channel and data (eg. on_message(channel, data))
        :type on_message: Callable[[str, dict], None]
        :param on_subscribe: The callback function for incoming subscribe messages it should accept two arguments: channel and data (eg. on_subscribe(channel, data))
        :type on_subscribe: Callable[[str, dict], None]
        :param ssl_skip_verify: Whether to skip SSL verification
        :type ssl_skip_verify: bool
        :param kwargs: Additional keyword arguments which will be passed to the websockets.sync.client.connect function
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
        self._websocket_thread = None
        self._websocket_stop_event = threading.Event()
        self._handler_queue = queue.Queue()
        self._handler_thread = None
        self._handler_stop_event = threading.Event()

    def register_handler(self, channel: str, handler: ChannelHandler):
        """
        Register a handler for a channel.

        The handler should be registered before subscribing to the channel.
        Otherwise, you're in risk of missing messages.
        The handler will be called with the data of the subscription.
        The handler will be called with the data of the message.

        Example:
            .. code-block:: python

                from rabbitx.ws.ws import WS
                from rabbitx.ws.channel_handler import ChannelHandler

                class OrderbookHandler(ChannelHandler):
                    def on_subscribe(self, data):
                        print(f"[ORDERBOOK] Subscribed: {data}")

                    def on_data(self, data):
                        print(f"[ORDERBOOK] Data: {data}")

                channel = "orderbook:BTC-USD"
                ws = WS(...)
                ws.register_handler(channel, OrderbookHandler(channel))
                ws.subscribe(channel)

                ws.start()

        :param channel: The channel to register the handler for
        :type channel: str
        :param handler: The handler to register
        :type handler: ChannelHandler
        """
        if channel not in self.handlers:
            self.handlers[channel] = []
        self.handlers[channel].append(handler)

        if not self.connected and channel not in self.channels:
            self.channels.append(channel)
            return

    def _connect(self):
        """
        Connect to the WebSocket server.
        """
        try:
            self.conn = connect(self.url, **self.connection_params)
            if DEBUG:
                logger.debug("Connected to %s", self.url)
            self.connected = True
            if self.token:
                self._authorize()
        except Exception as e:
            logger.error("Error in connect(): %s", e)
            raise

    def _disconnect(self):
        """
        Disconnect from the WebSocket server.
        """
        if self.conn:
            self.conn.close()
            self.conn = None

        self.authorized = False
        self.connected = False

    def send(self, message: str):
        """
        Send a message to the WebSocket server.

        :param message: The raw message to send (json string)
        :type message: str
        """
        self.conn.send(message)

    def request(self, message: dict, callback: Callable[[dict], None]):
        """
        Send a message to the WebSocket server with a callback function
        which will be called when the message is received.
        The callback function will be called with the received message as an argument.

        :param message: The message to send (json object)
        :type message: dict
        :param callback: The callback function to call when the message is received (eg. callback(message))
        :type callback: Callable[[dict], None]
        """
        self.message_id += 1
        self.promises[self.message_id] = callback
        message.update({"id": self.message_id})
        self.send(json.dumps(message))

    def _authorize(self):
        """
        Authorize the WebSocket connection.
        This method will send the authorize message to the WebSocket server
        and subscribe to the channels specified in the constructor.

        It's not necessary to call this method manually.
        It's called automatically when the connection is established.
        """

        def on_authorized(_):
            if DEBUG:
                logger.debug("Authorized")
            self.authorized = True
            for channel in self.channels:
                self.subscribe(channel)

        self.request({"connect": {"token": self.token, "name": "js"}}, on_authorized)

    def subscribe(self, channel: str):
        """
        Subscribe to a channel.

        There are two ways to handle messages from subscribed channels:
        1. Define the on_subscribe and on_message callbacks in the constructor.

            Example:

            .. code-block:: python

                from rabbitx.ws import WS

                def on_message(channel, data):
                    print(f"[MESSAGE] Channel: {channel}, Data: {data}")

                def on_subscribe(channel, data):
                    print(f"[SUBSCRIBED] Channel: {channel}, Data: {data}")

                ws = WS(
                    token=token,
                    on_subscribe=on_subscribe,
                    on_message=on_message,
                )

                ws.start()

        2. Register a handler for a channel using the register_handler method.

            Example:

            .. code-block:: python

                from rabbitx.ws.channel_handler import ChannelHandler
                from rabbitx.ws import WS

                class OrderbookHandler(ChannelHandler):
                    def on_subscribe(self, data):
                        print(f"[ORDERBOOK] Subscribed: {data}")

                    def on_data(self, data):
                        print(f"[ORDERBOOK] Data: {data}")

                channel = "orderbook:BTC-USD"
                ws = WS(...)
                ws.register_handler(channel, OrderbookHandler(channel))

                ws.start()

        :param channel: The channel to subscribe to
        :type channel: str
        """

        if not self.connected and channel not in self.channels:
            self.channels.append(channel)
            return

        def on_subscribe(msg):
            if DEBUG:
                logger.debug("Subscribed to %s", channel)
            self.subscribed[channel] = True
            data = msg["subscribe"]["data"]
            self._handler_queue.put(("subscribe", (channel, data)))

        self.request(
            {
                "subscribe": {"channel": channel},
            },
            on_subscribe,
        )

    def _handler_worker(self):
        """Worker thread that processes handler callbacks from the queue"""

        def handle_message(channel, data):
            if DEBUG:
                logger.debug(f"handle_message {channel} {data}")
            if self.on_message:
                self.on_message(channel, data)
            if channel in self.handlers:
                for handler in self.handlers[channel]:
                    handler.on_data(data)

        def handle_subscribe(channel, data):
            if DEBUG:
                logger.debug(f"handle_subscribe {channel} {data}")
            if self.on_subscribe:
                self.on_subscribe(channel, data)
            if channel in self.handlers:
                for handler in self.handlers[channel]:
                    handler.on_subscribe(data)

        while not self._handler_stop_event.is_set():
            try:
                handler_type, args = self._handler_queue.get(timeout=1)
                if DEBUG:
                    logger.debug(f"handler_type {handler_type} args {args}")
                if handler_type == "message":
                    channel, data = args
                    handle_message(channel, data)
                elif handler_type == "subscribe":
                    channel, data = args
                    handle_subscribe(channel, data)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error("Error in handler worker: %s", e)

    def _process_message(self, message):
        try:
            msg = json.loads(message)
        except Exception as e:
            logger.error("Error in json.loads(): %s", e)
            return

        if "id" in msg and msg["id"] in self.promises:
            self.promises[msg["id"]](msg)
            del self.promises[msg["id"]]
        elif dict_has_path(msg, "push.channel") and dict_has_path(msg, "push.pub.data"):
            channel = dict_get_path(msg, "push.channel")
            data = dict_get_path(msg, "push.pub.data")
            self._handler_queue.put(("message", (channel, data)))
        else:
            logger.error("Received unknown message: %s", msg)

    def _run(self):
        try:
            while not self._websocket_stop_event.is_set():
                try:
                    message = self.conn.recv(timeout=1)
                except TimeoutError:
                    continue

                if DEBUG:
                    logger.debug("Received message: %s", message)

                if message == "{}":
                    self.send("{}")
                    continue

                if "\n" in message:
                    for msg in message.split("\n"):
                        if msg.strip() == "":
                            continue
                        self._process_message(msg)
                else:
                    self._process_message(message)
        except ConnectionClosedOK as e:
            logger.error("Connection closed: %s", e)
            self._disconnect()
        except Exception as e:
            logger.error("Error in consume(): %s", e)
            raise

    def start(self):
        """
        Start the WebSocket connection in a separate thread.
        """

        def websocket_thread():
            try:
                logger.debug("Attempting to connect to WebSocket...")
                self._connect()
                logger.debug("WebSocket connected successfully")
                logger.debug("Starting to consume messages...")
                self._run()
            except Exception as e:
                logger.error("Error in WebSocket thread: %s", e)
            finally:
                self._disconnect()

        # Start handler thread
        self._handler_thread = threading.Thread(
            target=self._handler_worker, daemon=True
        )
        self._handler_thread.start()

        # Start WebSocket thread
        self._websocket_thread = threading.Thread(target=websocket_thread, daemon=True)
        self._websocket_thread.start()

    def stop(self):
        """
        Stop the WebSocket connection.
        """
        self._websocket_stop_event.set()
        self._handler_stop_event.set()
        if self.conn:
            try:
                self._disconnect()
            except Exception:
                pass
        if self._websocket_thread:
            self._websocket_thread.join()
            self._websocket_thread = None
        if self._handler_thread:
            self._handler_thread.join()
            self._handler_thread = None
