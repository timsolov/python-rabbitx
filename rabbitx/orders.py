from typing import TypedDict, Literal, Optional, List
from rabbitx.client import Client
from decimal import Decimal

OrderSide = Literal["long", "short"]
OrderStatus = Literal[
    "processing",
    "open",
    "closed",
    "rejected",
    "canceled",
    "canceling",
    "amending",
    "cancelingall",
    "placed",
]
OrderType = Literal[
    "limit",
    "market",
    "stop_loss",
    "take_profit",
    "stop_loss_limit",
    "take_profit_limit",
    "stop_market",
    "stop_limit",
    "cancel",
    "amend",
]
TypeInForce = Literal[
    "good_till_cancel", "immediate_or_cancel", "fill_or_kill", "post_only"
]


class CreateOrderParams(TypedDict):
    market_id: str
    type: OrderType
    side: OrderSide
    price: Decimal | str | float
    size: Decimal | str | float
    trigger_price: Optional[Decimal | str | float]
    time_in_force: Optional[TypeInForce]


class ListOrdersParams(TypedDict):
    market_id: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    status: Optional[List[OrderStatus]] = None
    order_id: Optional[str] = None
    client_order_id: Optional[str] = None
    order_type: Optional[List[OrderType]] = None


class AmendOrderParams(TypedDict):
    order_id: str
    market_id: str
    price: Optional[Decimal | float] = None
    size: Optional[Decimal | float] = None
    trigger_price: Optional[Decimal] = None
    size_percent: Optional[Decimal] = None


class CancelOrderParams(TypedDict):
    order_id: Optional[str] = None
    client_order_id: Optional[str] = None
    market_id: str


class Orders:
    """
    Orders class.

    This class is a wrapper around the RabbitX orders API.

    Attributes
    ----------
    client : Client
        The client object
    """

    def __init__(self, client: Client):
        self.client = client

    def create(self, **params: CreateOrderParams):
        """
        Create a new order

        https://docs.rabbitx.com/api-documentation/private-endpoints/orders#place-orders

        :param market_id: Market identifier
        :type market_id: str
        :param type: Order type ('limit' or 'market')
        :type type: OrderType
        :param side: Side of trade ('long' or 'short')
        :type side: OrderSide
        :param price: Order price
        :type price: Decimal | str
        :param size: Order size
        :type size: Decimal | str
        :param trigger_price: Optional trigger price
        :type trigger_price: Decimal | str
        :param time_in_force: Optional time in force parameter ('good_till_cancel', 'immediate_or_cancel', 'fill_or_kill', 'post_only')
        :type time_in_force: TypeInForce
        :return: The created order
        :rtype: dict

        Response:

        .. code-block:: python

            {
                "id": "BTC-USD@1191",
                "market_id": "BTC-USD",
                "profile_id": 88892,
                "status": "processing",
                "size": "0.0001",
                "price": "106000",
                "side": "short",
                "type": "limit",
                "is_liquidation": false,
                "client_order_id": "",
                "trigger_price": "0",
                "size_percent": "0",
                "time_in_force": "good_till_cancel"
            }
        """

        if isinstance(params["price"], Decimal) or isinstance(params["price"], str):
            params["price"] = float(params["price"])

        if isinstance(params["size"], Decimal) or isinstance(params["size"], str):
            params["size"] = float(params["size"])

        if "trigger_price" in params and (
            isinstance(params["trigger_price"], Decimal)
            or isinstance(params["trigger_price"], str)
        ):
            params["trigger_price"] = float(params["trigger_price"])

        response = self.client.post("/orders", body=params)
        response.raise_for_status()
        result = response.json()
        return result["result"][0]

    def list(self, **params: ListOrdersParams):
        """
        Get list of orders

        https://docs.rabbitx.com/api-documentation/private-endpoints/orders#get-account-order-status

        :param market_id: Market identifier (required if client_order_id is provided)
        :type market_id: str
        :param start_time: Filter orders after this timestamp (Unix timestamp)
        :type start_time: int
        :param end_time: Filter orders before this timestamp (Unix timestamp)
        :type end_time: int
        :param status: Filter by order status
        :type status: List[OrderStatus]
        :param order_id: Filter by specific order ID
        :type order_id: str
        :param client_order_id: Filter by client order ID
        :type client_order_id: str
        :param order_type: Filter by order types
        :type order_type: List[OrderType]
        :return: The list of orders
        :rtype: list

        Response:

        .. code-block:: python

            [
                {
                    "id": "BTC-USD@1193",
                    "profile_id": 88892,
                    "market_id": "BTC-USD",
                    "order_type": "limit",
                    "status": "open",
                    "price": "106000",
                    "size": "0.0001",
                    "initial_size": "0.0001",
                    "total_filled_size": "0",
                    "side": "short",
                    "timestamp": 1748776162875466,
                    "reason": "",
                    "client_order_id": "",
                    "trigger_price": "0",
                    "size_percent": "0",
                    "time_in_force": "good_till_cancel"
                }
            ]
        """
        response = self.client.get("/orders", params=params if params else None)
        response.raise_for_status()
        result = response.json()
        return result["result"]

    def amend(self, **params: AmendOrderParams):
        """
        Amend an existing order

        https://docs.rabbitx.com/api-documentation/private-endpoints/orders#amend-orders

        :param market_id: Market identifier
        :type market_id: str
        :param order_id: Order identifier
        :type order_id: str
        :param price: Optional new price
        :type price: Decimal | str | float
        :param size: Optional new size
        :type size: Decimal | str | float
        :param trigger_price: Optional new trigger price
        :type trigger_price: Decimal | str | float
        :param size_percent: Optional new size percentage
        :type size_percent: Decimal | str | float
        :return: The amended order
        :rtype: dict

        Response:

        .. code-block:: python

            {
                "id": "BTC-USD@1035",
                "market_id": "BTC-USD",
                "profile_id": 88892,
                "status": "amending",
                "price": "106001"
            }
        """

        if "price" in params and (
            isinstance(params["price"], Decimal) or isinstance(params["price"], str)
        ):
            params["price"] = float(params["price"])

        if "size" in params and (
            isinstance(params["size"], Decimal) or isinstance(params["size"], str)
        ):
            params["size"] = float(params["size"])

        if "trigger_price" in params and (
            isinstance(params["trigger_price"], Decimal)
            or isinstance(params["trigger_price"], str)
        ):
            params["trigger_price"] = float(params["trigger_price"])

        response = self.client.put("/orders", body=params)
        response.raise_for_status()
        result = response.json()
        return result["result"][0]

    def cancel(self, **params: CancelOrderParams):
        """
        Cancel specific order

        https://docs.rabbitx.com/api-documentation/private-endpoints/orders#cancel-orders

        :param market_id: Market identifier
        :type market_id: str
        :param order_id: Optional order identifier
        :type order_id: str
        :param client_order_id: Optional client order identifier
        :type client_order_id: str
        :return: The canceled order
        :rtype: dict

        Response:

        .. code-block:: python

            {
                "id": "BTC-USD@1035",
                "market_id": "BTC-USD",
                "profile_id": 88892,
                "status": "canceling",
                "client_order_id": ""
            }
        """
        response = self.client.delete("/orders", body=params)
        response.raise_for_status()
        result = response.json()
        return result["result"][0]

    def cancel_all(self):
        """Cancel all open orders

        https://docs.rabbitx.com/api-documentation/private-endpoints/orders#cancel-all-orders

        :return: The result of the cancellation
        :rtype: bool

        Response:

        .. code-block:: python

            true
        """
        response = self.client.delete("/orders/cancel_all", body={})
        response.raise_for_status()
        result = response.json()
        return bool(result["result"][0])
