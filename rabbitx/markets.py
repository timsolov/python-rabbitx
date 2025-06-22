import re
from typing import Optional, TypedDict, Literal, get_args
from .transport import Transport
from .response import single_or_fail, multiple_or_fail, MultipleResponse, SingleResponse
from .request import PaginationQuery

CandlesIntervals = Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"]

multipliers = {
    "m": 1,
    "h": 60,
    "d": 1440,
}


def parse_time_string(param):
    value, unit = re.match(r"^(\d+)([a-z]+)$", param).groups()
    return int(value) * multipliers[unit]


class CandlesParams(TypedDict):
    market_id: str
    start_time: int  # unix timestamp in seconds
    end_time: int  # unix timestamp in seconds
    period: CandlesIntervals  # 1m, 5m, 15m, 30m, 1h, 4h, 1d


class MarketsBase:
    def __init__(self, transport: Transport):
        self.transport = transport

    def _validate_candles_params(self, params: CandlesParams):
        if params["start_time"] >= params["end_time"]:
            raise ValueError("Start time must be less than end time")
        if params["period"] not in get_args(CandlesIntervals):
            raise ValueError(f"Invalid period: {params['period']}")

    def _prepare_candles_request(self, params: CandlesParams) -> dict:
        period_seconds = parse_time_string(params["period"])
        return {
            "market_id": params["market_id"],
            "timestamp_from": params["start_time"],
            "timestamp_to": params["end_time"],
            "period": period_seconds,
        }


class Markets(MarketsBase):
    """
    Markets class.

    This class is a wrapper around the RabbitX markets API.

    Attributes
    ----------
    transport : Transport
        The transport object
    """

    def info(self, market_id: str) -> SingleResponse:
        """
        Get market info

        https://docs.rabbitx.com/api-documentation/public-endpoints/market-info#market-info

        :param market_id: Market ID (e.g. 'BTC-USD')
        :type market_id: str
        :return: The market info
        :rtype: SingleResponse

        Response:

        .. code-block:: python

            {
                "id": "BTC-USD",
                "status": "active",
                "min_tick": "1",
                "min_order": "0.0001",
                "best_bid": "0",
                "best_ask": "0",
                "market_price": "106000",
                "index_price": "104124",
                "last_trade_price": "106000",
                "fair_price": "106092",
                "instant_funding_rate": "0",
                "last_funding_rate_basis": "0",
                "last_update_time": 1748777590845538,
                "last_update_sequence": 96,
                "average_daily_volume_q": "0.0109",
                "last_funding_update_time": 1748775600217611,
                "icon_url": "",
                "market_title": "",
                "base_currency": "BTC",
                "quote_currency": "USD",
                "product_type": "perpetual",
                "open_interest": "42.4332",
                "next_funding_rate_timestamp": 1748779200,
                "average_daily_volume": "21.2",
                "last_trade_price_24high": "106000",
                "last_trade_price_24low": "106000",
                "last_trade_price_24h_change_premium": "0",
                "last_trade_price_24h_change_basis": "0",
                "average_daily_volume_change_premium": "-212",
                "average_daily_volume_change_basis": "-0.90909090909090909091",
                "market_cap": "2067876760453"
            }
        """
        response = self.transport.get("/markets", params={"market_id": market_id})
        response.raise_for_status()
        return single_or_fail(response.json())

    def list(self, *, pagination: Optional[PaginationQuery] = None) -> MultipleResponse:
        """
        Get list of markets

        https://docs.rabbitx.com/api-documentation/public-endpoints/market-info#market-info

        :return: The list of markets
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "id": "BTC-USD",
                    "status": "active",
                    "min_tick": "1",
                    "min_order": "0.0001",
                    "best_bid": "0",
                    "best_ask": "0",
                    "market_price": "106000",
                    "index_price": "104124",
                    "last_trade_price": "106000",
                    "fair_price": "106092",
                    "instant_funding_rate": "0",
                    "last_funding_rate_basis": "0",
                    "last_update_time": 1748777590845538,
                    "last_update_sequence": 96,
                    "average_daily_volume_q": "0.0109",
                    "last_funding_update_time": 1748775600217611,
                    "icon_url": "",
                    "market_title": "",
                    "base_currency": "BTC",
                    "quote_currency": "USD",
                    "product_type": "perpetual",
                    "open_interest": "42.4332",
                    "next_funding_rate_timestamp": 1748779200,
                    "average_daily_volume": "21.2",
                    "last_trade_price_24high": "106000",
                    "last_trade_price_24low": "106000",
                    "last_trade_price_24h_change_premium": "0",
                    "last_trade_price_24h_change_basis": "0",
                    "average_daily_volume_change_premium": "-212",
                    "average_daily_volume_change_basis": "-0.90909090909090909091",
                    "market_cap": "2067876760453"
                }
            ]
        """
        response = self.transport.get("/markets", params=pagination)
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.list(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    def candles(self, **params: CandlesParams) -> MultipleResponse:
        """
        Get candles

        https://docs.rabbitx.com/api-documentation/public-endpoints/candles#candles

        :param market_id: Market ID (e.g. 'BTC-USD')
        :type market_id: str
        :param start_time: Start time unix timestamp in seconds (e.g. 1748777590)
        :type start_time: int
        :param end_time: End time unix timestamp in seconds (e.g. 1748777590)
        :type end_time: int
        :param period: Period (e.g. '1m', '5m', '15m', '30m', '1h', '4h', '1d')
        :type period: CandlesIntervals

        :return: The candles
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "time": 1750608000,
                    "low": "98695",
                    "high": "99517",
                    "open": "98923",
                    "close": "99496",
                    "volume": "9198752.694"
                },
                {
                    "time": 1750604400,
                    "low": "98913",
                    "high": "99835",
                    "open": "99632",
                    "close": "98923",
                    "volume": "10261500.9123"
                }
            ]
        """

        self._validate_candles_params(params)
        request_params = self._prepare_candles_request(params)
        response = self.transport.get("/candles", params=request_params)
        response.raise_for_status()
        return multiple_or_fail(response.json())


class AsyncMarkets(MarketsBase):
    __doc__ = Markets.__doc__

    async def info(self, market_id: str) -> SingleResponse:
        response = await self.transport.get("/markets", params={"market_id": market_id})
        response.raise_for_status()
        return single_or_fail(response.json())

    info.__doc__ = Markets.info.__doc__

    async def list(
        self, *, pagination: Optional[PaginationQuery] = None
    ) -> MultipleResponse:
        response = await self.transport.get("/markets", params=pagination)
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.list(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    list.__doc__ = Markets.list.__doc__

    async def candles(self, **params: CandlesParams) -> MultipleResponse:
        self._validate_candles_params(params)
        request_params = self._prepare_candles_request(params)
        response = await self.transport.get("/candles", params=request_params)
        response.raise_for_status()
        return multiple_or_fail(response.json())

    candles.__doc__ = Markets.candles.__doc__
