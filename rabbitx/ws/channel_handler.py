class ChannelHandler:
    """
    ChannelHandler is the base class for all channel handlers.
    It provides methods that will be called when messages are received on subscribed channels.

    Example:
        .. code-block:: python

            from rabbitx.ws.channel_handler import ChannelHandler

            class MyHandler(ChannelHandler):
                def on_subscribe(self, data: dict):
                    print(f"[SUBSCRIBED] Channel: {self.name}, Data: {data}")

                def on_data(self, data: dict):
                    print(f"[DATA] Channel: {self.name}, Data: {data}")

    """

    def __init__(self, name: str):
        """
        Initialize the ChannelHandler

        :param name: The name of the channel (useful for logging)
        :type name: str
        """
        self.name = name

    def on_subscribe(self, data: dict):
        """Called when subscription to the channel is confirmed

        :param data: Subscription confirmation data
        :type data: dict
        """
        pass

    def on_data(self, data: dict):
        """Called when new data arrives on the channel

        :param data: The message data
        :type data: dict
        """
        pass


class AsyncChannelHandler:
    """
    AsyncChannelHandler is the base class for all async channel handlers.
    It provides async methods that will be called when messages are received on subscribed channels.

    Example:
        .. code-block:: python

            from rabbitx.ws.channel_handler import AsyncChannelHandler

            class MyAsyncHandler(AsyncChannelHandler):
                async def on_data(self, data: dict):
                    # Can perform async operations here
                    await create_order(...)

                async def on_subscribe(self, data: dict):
                    # Can perform async operations here
                    await initialize_something(...)
    """

    def __init__(self, name: str):
        """
        Initialize the AsyncChannelHandler

        :param name: The name of the channel (useful for logging)
        :type name: str
        """
        self.name = name

    async def on_subscribe(self, data: dict):
        """Called when subscription to the channel is confirmed

        :param data: Subscription confirmation data
        :type data: dict
        """
        pass

    async def on_data(self, data: dict):
        """Called when new data arrives on the channel

        :param data: The message data
        :type data: dict
        """
        pass
