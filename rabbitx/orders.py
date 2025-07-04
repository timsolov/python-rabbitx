from typing import TypedDict, Literal, Optional, List, Union
from .transport import Transport
from decimal import Decimal
from .response import single_or_fail, multiple_or_fail, MultipleResponse, SingleResponse
from .request import PaginationQuery

OrderSide = Literal[
    "long",
    "short",
]

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
    "good_till_cancel",
    "immediate_or_cancel",
    "fill_or_kill",
    "post_only",
]


class CreateOrderParams(TypedDict):
    market_id: str
    type: OrderType
    side: OrderSide
    price: Union[Decimal, str, float]
    size: Union[Decimal, str, float]
    trigger_price: Optional[Union[Decimal, str, float]]
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
    client_order_id: Optional[str] = None
    market_id: str
    price: Optional[Union[Decimal, float]] = None
    size: Optional[Union[Decimal, float]] = None
    trigger_price: Optional[Decimal] = None
    size_percent: Optional[Decimal] = None


class CancelOrderParams(TypedDict):
    order_id: Optional[str] = None
    client_order_id: Optional[str] = None
    market_id: str


class FillsParams(TypedDict):
    market_id: Optional[str]
    start_time: Optional[int]
    end_time: Optional[int]


class BaseOrders:
    def __init__(self, transport: Transport):
        self.transport = transport

    def _fix_create_params(self, params: CreateOrderParams):
        if "price" in params and (
            isinstance(params["price"], Decimal) or isinstance(params["price"], str)
        ):
            params["price"] = float(params["price"])

        if isinstance(params["size"], Decimal) or isinstance(params["size"], str):
            params["size"] = float(params["size"])

        if "trigger_price" in params and (
            isinstance(params["trigger_price"], Decimal)
            or isinstance(params["trigger_price"], str)
        ):
            params["trigger_price"] = float(params["trigger_price"])

    def _fix_amend_params(self, params: AmendOrderParams):
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


class Orders(BaseOrders):
    """
    Orders class.

    This class is a wrapper around the RabbitX orders API.

    Attributes
    ----------
    transport : Transport
        The transport object
    """

    def create(self, **params: CreateOrderParams) -> SingleResponse:
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
        :rtype: SingleResponse

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
        self._fix_create_params(params)
        response = self.transport.post("/orders", body=params)
        response.raise_for_status()
        return single_or_fail(response.json())

    def list(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        **params: ListOrdersParams,
    ) -> MultipleResponse:
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
        :param pagination: Optional pagination parameters
        :type pagination: PaginationQuery
        :return: The list of orders
        :rtype: MultipleResponse

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
        request_params = dict(params)
        if pagination:
            request_params.update(pagination)

        response = self.transport.get(
            "/orders", params=request_params if request_params else None
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.list(pagination=pagination, **params)

        return multiple_or_fail(response.json(), next_page_func)

    def amend(self, **params: AmendOrderParams) -> SingleResponse:
        """
        Amend an existing order

        https://docs.rabbitx.com/api-documentation/private-endpoints/orders#amend-orders

        :param market_id: Market identifier
        :type market_id: str
        :param order_id: Order identifier
        :type order_id: str
        :param price: Optional new price
        :type price: Union[Decimal, str, float]
        :param size: Optional new size
        :type size: Union[Decimal, str, float]
        :param trigger_price: Optional new trigger price
        :type trigger_price: Union[Decimal, str, float]
        :param size_percent: Optional new size percentage
        :type size_percent: Union[Decimal, str, float]
        :return: The amended order
        :rtype: SingleResponse

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

        self._fix_amend_params(params)
        response = self.transport.put("/orders", body=params)
        response.raise_for_status()
        return single_or_fail(response.json())

    def cancel(self, **params: CancelOrderParams) -> SingleResponse:
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
        :rtype: SingleResponse

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
        response = self.transport.delete("/orders", body=params)
        response.raise_for_status()
        return single_or_fail(response.json())

    def cancel_all(self) -> SingleResponse:
        """Cancel all open orders

        https://docs.rabbitx.com/api-documentation/private-endpoints/orders#cancel-all-orders

        :return: The result of the cancellation
        :rtype: bool

        Response:

        .. code-block:: python

            true
        """
        response = self.transport.delete("/orders/cancel_all", body={})
        response.raise_for_status()
        return single_or_fail(response.json())

    def fills(
        self, *, pagination: Optional[PaginationQuery] = None, **params: FillsParams
    ) -> MultipleResponse:
        """
        Get all fills

        :return: The fills
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "id": "BTC-USD-82",
                    "profile_id": 84980,
                    "market_id": "BTC-USD",
                    "order_id": "BTC-USD@1147",
                    "timestamp": 1749801319584077,
                    "trade_id": "BTC-USD-81",
                    "price": "103120",
                    "size": "0.0002",
                    "side": "short",
                    "is_maker": true,
                    "fee": "0",
                    "liquidation": false,
                    "client_order_id": ""
                }
            ]
        """

        request_params = dict(params)
        if pagination:
            request_params.update(pagination)

        response = self.transport.get(
            "/fills", params=request_params if request_params else None
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.fills(pagination=pagination, **params)

        return multiple_or_fail(response.json(), next_page_func)


class AsyncOrders(BaseOrders):
    __doc__ = Orders.__doc__

    async def create(self, **params: CreateOrderParams) -> SingleResponse:
        self._fix_create_params(params)
        response = await self.transport.post("/orders", body=params)
        response.raise_for_status()
        return single_or_fail(response.json())

    create.__doc__ = Orders.create.__doc__

    async def list(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        **params: ListOrdersParams,
    ) -> MultipleResponse:
        request_params = dict(params)
        if pagination:
            request_params.update(pagination)

        response = await self.transport.get(
            "/orders", params=request_params if request_params else None
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.list(pagination=pagination, **params)

        return multiple_or_fail(response.json(), next_page_func)

    list.__doc__ = Orders.list.__doc__

    async def amend(self, **params: AmendOrderParams) -> SingleResponse:
        self._fix_amend_params(params)
        response = await self.transport.put("/orders", body=params)
        response.raise_for_status()
        return single_or_fail(response.json())

    amend.__doc__ = Orders.amend.__doc__

    async def cancel(self, **params: CancelOrderParams) -> SingleResponse:
        response = await self.transport.delete("/orders", body=params)
        response.raise_for_status()
        return single_or_fail(response.json())

    cancel.__doc__ = Orders.cancel.__doc__

    async def cancel_all(self) -> SingleResponse:
        response = await self.transport.delete("/orders/cancel_all", body={})
        response.raise_for_status()
        return single_or_fail(response.json())

    cancel_all.__doc__ = Orders.cancel_all.__doc__

    async def fills(
        self, *, pagination: Optional[PaginationQuery] = None, **params: FillsParams
    ) -> MultipleResponse:
        request_params = dict(params)
        if pagination:
            request_params.update(pagination)

        response = await self.transport.get(
            "/fills", params=request_params if request_params else None
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.fills(pagination=pagination, **params)

        return multiple_or_fail(response.json(), next_page_func)

    fills.__doc__ = Orders.fills.__doc__
