from typing import Callable
from .channel_handler import ChannelHandler

class OpenedOrders(ChannelHandler):
    orders: dict
    on_update: Callable

    def __init__(self, on_update: Callable[[str, dict], None] = None):
        """
        OpenOrders is a class that represents the open orders for a given market.
        It is used to keep track of the orders for a given market.
        It is also used to update the orders when the orders are updated.

        :param on_update: A callback function that is called when the orders are updated. on_update(market_id, order)
        :type on_update: Callable[[str, dict], None]
        """
        self.orders = {}
        self.on_update = on_update

        super().__init__(name="opened_orders")

    def consume(self, data):
        """
        Consume the orders from the data.

        :param data: The data to consume. data['orders'] is a list of orders.
        :type data: dict
        """
        if not 'orders' in data:
            return
        
        for order in data['orders']:
            if not 'market_id' in order or not 'id' in order:
                continue

            market_id = order['market_id']
            order_id = order['id']

            if not market_id in self.orders:
                self.orders[market_id] = {}

            if not order_id in self.orders[market_id]:
                self.orders[market_id][order_id] = order
                
            if order['status'] in ['closed', 'rejected', 'canceled', 'canceling']:
                del self.orders[market_id][order_id]
            else:
                self.orders[market_id][order_id] = order

            if self.on_update:
                self.on_update(order)

    def get_orders(self) -> dict:
        """
        Get all orders

        :return: A list of orders
        :rtype: list[dict]
        """
        orders = []
        for market_id in self.orders:
            for order_id in self.orders[market_id]:
                orders.append(self.orders[market_id][order_id])
        return orders
    
    def get_order(self, market_id: str, order_id: str) -> dict | None:
        """
        Get an order by market_id and order_id

        :param market_id: The market ID
        :type market_id: str
        :param order_id: The order ID
        :type order_id: str
        :return: The order
        :rtype: dict | None
        """
        
        return self.orders.get(market_id, {}).get(order_id, None)

    def on_subscribe(self, data: dict):
        self.consume(data)

    def on_data(self, data: dict):
        self.consume(data)