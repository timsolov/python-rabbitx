from .channel_handler import ChannelHandler
from rabbitx.xutils import dict_get_path, dict_has_path
from typing import Callable
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
    """

    def __init__(
        self,
        token: str,
        network: str = None,
        url: str = None,
        channels: list[str] = {},
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

        :param channel: The channel to register the handler for
        :type channel: str
        :param handler: The handler to register
        :type handler: ChannelHandler
        """
        if channel not in self.handlers:
            self.handlers[channel] = []
        self.handlers[channel].append(handler)

    def connect(self):
        """
        Connect to the WebSocket server.
        """
        try:
            self.conn = connect(self.url, **self.connection_params)
            if DEBUG:
                logger.debug("Connected to %s", self.url)
            if self.token:
                self.authorize()
        except Exception as e:
            logger.error("Error in connect(): %s", e)
            raise

    def disconnect(self):
        """
        Disconnect from the WebSocket server.
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def send(self, message: str):
        """
        Send a message to the WebSocket server.

        :param message: The message to send
        :type message: str
        """
        self.conn.send(message)

    def send_with_handler(self, message: dict, handler: Callable[[dict], None]):
        """
        Send a message to the WebSocket server with a handler.

        :param message: The message to send
        :type message: dict
        :param handler: The handler to register
        """
        self.message_id += 1
        self.promises[self.message_id] = handler
        message.update({"id": self.message_id})
        self.send(json.dumps(message))

    def authorize(self):
        """
        Authorize the WebSocket connection.
        """

        def on_authorized(_):
            if DEBUG:
                logger.debug("Authorized")
            self.authorized = True
            for channel in self.channels:
                self.subscribe(channel)

        self.send_with_handler(
            {"connect": {"token": self.token, "name": "js"}}, on_authorized
        )

    def subscribe(self, channel: str):
        """
        Subscribe to a channel.

        :param channel: The channel to subscribe to
        :type channel: str
        """

        def on_subscribe(msg):
            if DEBUG:
                logger.debug("Subscribed to %s", channel)
            self.subscribed[channel] = True
            data = msg["subscribe"]["data"]
            self._handler_queue.put(("subscribe", (channel, data)))

        self.send_with_handler(
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

    def single_message(self, message):
        """
        Process a single message.

        :param message: The message to process
        :type message: str
        """
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

    def consume(self):
        """
        Consume messages from the WebSocket server.
        """
        try:
            while not self._websocket_stop_event.is_set():
                message = self.conn.recv()
                if DEBUG:
                    logger.debug("Received message: %s", message)
                if message == "{}":
                    self.send("{}")
                    continue
                if "\n" in message:
                    for msg in message.split("\n"):
                        if msg.strip() == "":
                            continue
                        self.single_message(msg)
                else:
                    self.single_message(message)
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
                self.connect()
                logger.debug("WebSocket connected successfully")
                logger.debug("Starting to consume messages...")
                self.consume()
            except Exception as e:
                logger.error("Error in WebSocket thread: %s", e)
            finally:
                self.disconnect()

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
                self.conn.close()
            except Exception:
                pass
        if self._websocket_thread:
            self._websocket_thread.join()
            self._websocket_thread = None
        if self._handler_thread:
            self._handler_thread.join()
            self._handler_thread = None
