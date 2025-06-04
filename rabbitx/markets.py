from rabbitx.client import Client


class Markets:
    """
    Markets class.

    This class is a wrapper around the RabbitX markets API.

    Attributes
    ----------
    client : Client
        The client object
    """

    def __init__(self, client: Client):
        self.client = client

    def info(self, market_id: str):
        """
        Get market info

        https://docs.rabbitx.com/api-documentation/public-endpoints/market-info#market-info

        :param market_id: Market ID (e.g. 'BTC-USD')
        :type market_id: str
        :return: The market info
        :rtype: dict

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
        response = self.client.get("/markets", params={"market_id": market_id})
        response.raise_for_status()
        result = response.json()
        return result["result"][0]

    def list(self):
        """
        Get list of markets

        https://docs.rabbitx.com/api-documentation/public-endpoints/market-info#market-info

        :return: The list of markets
        :rtype: list

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
        response = self.client.get("/markets")
        response.raise_for_status()
        result = response.json()
        return result["result"]
