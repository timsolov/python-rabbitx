from BTrees.OOBTree import OOBTree as BTree
from typing import Callable
from .channel_handler import ChannelHandler
from decimal import Decimal

zero = Decimal("0")

class Orderbook(ChannelHandler):
    def __init__(self, market_id: str, on_update: Callable[[str, str, Decimal, Decimal], None] = None):
        """
        Orderbook is a class that represents the orderbook for a given market.
        It is used to keep track of the orderbook for a given market.
        It is also used to update the orderbook when the orderbook is updated.

        :param market_id: The market id of the orderbook.
        :type market_id: str
        :param on_update: A callback function that is called when the orderbook is updated. on_update(market_id, side, price, amount)
        :type on_update: Callable[[str, str, Decimal, Decimal], None]
        """
        self.orderbook = {
            'asks': BTree(),
            'bids': BTree(),
        }
        self.market_id = market_id
        self.on_update = on_update

        super().__init__(name='orderbook:'+market_id)

    def consume(self, data):
        """
        Consume the orderbook from the data.

        :param data: The data to consume. data['asks'] and data['bids'] are lists of [price, amount].
        :type data: dict
        """
        if 'asks' in data:
            for price, amount in data['asks']:
                price = Decimal(price)
                amount = Decimal(amount)
                self.orderbook['asks'].update({price: amount})
                if amount == zero:
                    self.orderbook['asks'].pop(price)
                if self.on_update:
                    self.on_update(self.market_id, 'short', Decimal(price), Decimal(amount))

        if 'bids' in data:
            for price, amount in data['bids']:
                price = Decimal(price)
                amount = Decimal(amount)
                self.orderbook['bids'].update({price: amount})
                if amount == zero:
                    self.orderbook['bids'].pop(price)
                if self.on_update:
                    self.on_update(self.market_id, 'long', Decimal(price), Decimal(amount))

    def best_ask(self) -> float | None:
        """
        Get the best ask price

        :return: The best ask price
        :rtype: float | None
        """
        return self.orderbook['asks'].minKey() if len(self.orderbook['asks']) > 0 else None
    
    def best_bid(self) -> float | None:
        """
        Get the best bid price

        :return: The best bid price
        :rtype: float | None
        """
        return self.orderbook['bids'].maxKey() if len(self.orderbook['bids']) > 0 else None
    
    def on_subscribe(self, data: dict):
        self.consume(data)

    def on_data(self, data: dict):
        self.consume(data)

