from typing import Callable, Union
from .channel_handler import ChannelHandler


class Positions(ChannelHandler):
    def __init__(self, on_update: Callable[[str, dict], None] = None):
        """
        Positions is a class that represents the positions for a given market.
        It is used to keep track of the positions for a given market.
        It is also used to update the positions when the positions are updated.

        :param on_update: A callback function that is called when the positions are updated. on_update(market_id, position)
        :type on_update: Callable[[str, dict], None]
        """

        self.positions = {}
        self.on_update = on_update

        super().__init__(name="positions")

    def consume(self, data):
        """
        Consume the positions from the data.

        :param data: The data to consume. data['positions'] is a list of positions.
        :type data: dict
        """
        if "positions" not in data:
            return

        for position in data["positions"]:
            if "market_id" not in position:
                continue
            market_id = position["market_id"]
            self.positions[market_id] = position
            if float(position["size"]) == 0:
                del self.positions[market_id]
            if self.on_update:
                self.on_update(market_id, position)

    def get_position(self, market_id: str) -> Union[dict, None]:
        """
        Get a position by market_id

        :param market_id: The market ID
        :type market_id: str
        :return: The position
        :rtype: dict | None
        """
        return self.positions.get(market_id, None)

    def get_positions(self) -> dict:
        """
        Get all positions

        :return: A list of positions
        :rtype: list[dict]
        """
        return self.positions

    def on_subscribe(self, data: dict):
        self.consume(data)

    def on_data(self, data: dict):
        self.consume(data)
