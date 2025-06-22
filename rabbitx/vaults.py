from typing import Literal, List, Optional
from .transport import Transport, AsyncTransport
from .response import multiple_or_fail, MultipleResponse
from .request import PaginationQuery


class Vaults:
    """
    Vaults class.

    This class is a wrapper around the RabbitX vaults API.

    Attributes
    ----------
    transport : Transport
        The transport object
    """

    def __init__(self, transport: Transport):
        self.transport = transport

    def list(self, *, pagination: Optional[PaginationQuery] = None) -> MultipleResponse:
        """Get list of vaults

        :return: List of vaults
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "vault_profile_id": 89477,
                    "wallet": "0xf4d12bde8a4feafa42b1ae35a5ad97e7e9f38fa4",
                    "exchange_id": "rbx",
                    "account_equity": "392992.70864336301523506620504411900743312796",
                    "total_shares": "353117.88623907424802934634129460965456",
                    "share_price": "1.11292609874564961873728472095448508016",
                    "apy": "0.33877829623694885621185416286345524048",
                    "status": "active",
                    "performance_fee": "0",
                    "manager_name": "RabbitX",
                    "vault_name": "Liquidity Pool (RLP)",
                    "inception_timestamp": 1739697529877607
                }
            ]
        """
        response = self.transport.get("/vaults", params=pagination)
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.list(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    def holdings(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        vault_profile_id: int = None,
    ) -> MultipleResponse:
        """Get holdings in vaults for current profile

        :param vault_profile_id: Vault profile ID (optional)
        :type vault_profile_id: int
        :return: Holdings in vaults for current profile
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "staker_profile_id": 19073,
                    "vault_profile_id": 89477,
                    "status": "active",
                    "vault_name": "Liquidity Pool (RLP)",
                    "manager_name": "RabbitX",
                    "inception_timestamp": 1739697529877607,
                    "staker_holdings": "13.840515156389604236",
                    "shares": "12.441431548466179397",
                    "user_nav": "13.8405151563896044",
                    "net_withdrawable": "13.8405151563896044",
                    "performance_charge": "0",
                    "performance_fee": "0"
                }
            ]
        """

        request_params = dict(pagination)
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id

        response = self.transport.get(
            "/vaults/holdings",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.holdings(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    def all_balanceops(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        ops_types: List[str],
        vault_profile_id: int = None,
    ) -> MultipleResponse:
        """Get all balance operations

        :param ops_types: List of operation types to filter by (required) ['stake', 'unstake']
        :param vault_profile_id: Vault profile ID (optional)
        :return: All balance operations
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "id": "fd0c14b2-468e-4648-8e17-b66f2d93c469",
                    "ops_type": "stake",
                    "ops_sub_type": "stake",
                    "staker_profile_id": 90390,
                    "vault_profile_id": 89477,
                    "wallet": "0x1d6513f43bd9e3353e131d35fb2f1ecfde04f34a",
                    "exchange_id": "rbx_sonic",
                    "status": "success",
                    "vault_name": "Liquidity Pool (RLP)",
                    "manager_name": "RabbitX",
                    "inception_timestamp": 1739697529877607,
                    "timestamp": 1748810404845488,
                    "stake_usdt": "529.549244",
                    "stake_shares": "474.9827083683115047604560339517796888",
                    "unstake_shares": "0",
                    "unstake_usdt": "0",
                    "unstake_fee_usdt": "0"
                }
            ]
        """

        request_params = dict(pagination)
        if ops_types:
            request_params["ops_type"] = ops_types
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id

        response = self.transport.get(
            "/vaults/all-balanceops",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.all_balanceops(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    def user_balanceops(
        self,
        *,
        ops_types: List[str],
        vault_profile_id: int = None,
        pagination: Optional[PaginationQuery] = None,
    ) -> MultipleResponse:
        """Get user balance operations

        :param ops_types: List of operation types to filter by (required) ['stake', 'unstake']
        :param vault_profile_id: Vault profile ID (optional)
        :return: User balance operations
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "id": "df4c1df7-b652-4db4-9c19-908b71e12011",
                    "ops_type": "stake",
                    "ops_sub_type": "stake",
                    "staker_profile_id": 19073,
                    "vault_profile_id": 89477,
                    "wallet": "0xf4d12bde8a4feafa42b1ae35a5ad97e7e9f38fa4",
                    "exchange_id": "rbx",
                    "status": "success",
                    "vault_name": "Liquidity Pool (RLP)",
                    "manager_name": "RabbitX",
                    "inception_timestamp": 1739697529877607,
                    "timestamp": 1747995183565275,
                    "stake_usdt": "0.94",
                    "stake_shares": "0.86177189829474961553052805547130963893",
                    "unstake_shares": "0",
                    "unstake_usdt": "0",
                    "unstake_fee_usdt": "0"
                }
            ]
        """

        request_params = dict(pagination)
        if ops_types:
            request_params["ops_type"] = ops_types
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id

        response = self.transport.get(
            "/vaults/balanceops",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.user_balanceops(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    def history(
        self,
        *,
        vault_profile_id: int,
        type: Literal["share_price", "nav"] = "nav",
        range: Literal["1h", "1d", "1w", "1m", "1y", "all"] = "1d",
    ) -> MultipleResponse:
        """Get history of a vault

        :param vault_profile_id: Vault profile ID (required)
        :param type: Type of history to get (optional), default is 'nav' ['share_price', 'nav']
        :param range: Range of history to get (optional), default is '1d' ['1h', '1d', '1w', '1m', '1y', 'all']
        :return: History of a vault in timeseries format
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "time": 1748807100000000,
                    "value": "408507.17718666092962904598516940983460282196"
                },
                {
                    "time": 1748808000000000,
                    "value": "408574.50129083517707534985216940983460468816"
                }
            ]
        """

        request_params = {}
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id
        if type:
            request_params["type"] = type
        if range:
            request_params["range"] = range

        response = self.transport.get(
            "/vaults/history",
            params=request_params if request_params else None,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.history(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    def fills(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        vault_profile_id: int,
        start_time: int = None,
        end_time: int = None,
    ) -> MultipleResponse:
        """Get fills for a vault

        :param vault_profile_id: Vault profile ID (required)
        :param start_time: Start time unix timestamp in seconds (optional)
        :param end_time: End time unix timestamp in seconds (optional)
        :return: Fills for a vault
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "id": "XRP-USD-40175189",
                    "profile_id": 89477,
                    "market_id": "XRP-USD",
                    "order_id": "XRP-USD@6220462911",
                    "timestamp": 1748892911504558,
                    "trade_id": "XRP-USD-40175187",
                    "price": "2.1595",
                    "size": "890",
                    "side": "long",
                    "is_maker": false,
                    "fee": "0",
                    "liquidation": false,
                    "client_order_id": "MM:1748872473896765"
                }
            ]
        """

        request_params = dict(pagination)
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id
        if start_time:
            request_params["start_time"] = (
                start_time * 1000000
            )  # convert to microseconds
        if end_time:
            request_params["end_time"] = end_time * 1000000  # convert to microseconds

        response = self.transport.get(
            "/vaults/fills",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.fills(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    def funding(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        vault_profile_id: int,
        start_time: int = None,
        end_time: int = None,
    ) -> MultipleResponse:
        """Get funding for a vault

        :param vault_profile_id: Vault profile ID (required)
        :param start_time: Start time unix timestamp in seconds (optional)
        :param end_time: End time unix timestamp in seconds (optional)
        :return: Funding for a vault
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "id": "3fff5c42-3604-4a9a-b9ce-4a96aae8e596",
                    "status": "success",
                    "reason": "",
                    "txhash": "",
                    "profile_id": 89477,
                    "wallet": "",
                    "ops_type": "funding",
                    "ops_id2": "3fff5c42-3604-4a9a-b9ce-4a96aae8e596",
                    "amount": "-0.000007883425422517471",
                    "timestamp": 1748890825585867,
                    "due_block": 0,
                    "shard_id": "LAYER-USD"
                }
            ]
        """

        request_params = dict(pagination)
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id
        if start_time:
            request_params["start_time"] = (
                start_time * 1000000
            )  # convert to microseconds
        if end_time:
            request_params["end_time"] = end_time * 1000000  # convert to microseconds

        response = self.transport.get(
            "/vaults/funding",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.funding(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)


class AsyncVaults:
    __doc__ = Vaults.__doc__

    def __init__(self, transport: AsyncTransport):
        self.transport = transport

    async def list(
        self, *, pagination: Optional[PaginationQuery] = None
    ) -> MultipleResponse:
        response = await self.transport.get("/vaults", params=pagination)
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.list(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    list.__doc__ = Vaults.list.__doc__

    async def holdings(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        vault_profile_id: int = None,
    ) -> MultipleResponse:
        request_params = dict(pagination)
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id

        response = await self.transport.get(
            "/vaults/holdings",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.holdings(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    holdings.__doc__ = Vaults.holdings.__doc__

    async def all_balanceops(
        self,
        *,
        ops_types: List[str],
        vault_profile_id: int = None,
    ) -> MultipleResponse:
        request_params = {}
        if ops_types:
            request_params["ops_type"] = ops_types
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id

        response = await self.transport.get(
            "/vaults/all-balanceops",
            params=request_params if request_params else None,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.all_balanceops(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    all_balanceops.__doc__ = Vaults.all_balanceops.__doc__

    async def user_balanceops(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        ops_types: List[str],
        vault_profile_id: int = None,
    ) -> MultipleResponse:
        request_params = dict(pagination)
        if ops_types:
            request_params["ops_type"] = ops_types
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id

        response = await self.transport.get(
            "/vaults/balanceops",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.user_balanceops(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    user_balanceops.__doc__ = Vaults.user_balanceops.__doc__

    async def history(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        vault_profile_id: int,
        type: Literal["share_price", "nav"] = "nav",
        range: Literal["1h", "1d", "1w", "1m", "1y", "all"] = "1d",
    ) -> MultipleResponse:
        request_params = dict(pagination)
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id
        if type:
            request_params["type"] = type
        if range:
            request_params["range"] = range

        response = await self.transport.get(
            "/vaults/history",
            params={"vault_profile_id": vault_profile_id, "type": type, "range": range},
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.history(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    history.__doc__ = Vaults.history.__doc__

    async def fills(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        vault_profile_id: int,
        start_time: int = None,
        end_time: int = None,
    ) -> MultipleResponse:
        request_params = dict(pagination)
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id
        if start_time:
            request_params["start_time"] = (
                start_time * 1000000
            )  # convert to microseconds
        if end_time:
            request_params["end_time"] = end_time * 1000000  # convert to microseconds

        response = await self.transport.get(
            "/vaults/fills",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.fills(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    fills.__doc__ = Vaults.fills.__doc__

    async def funding(
        self,
        *,
        pagination: Optional[PaginationQuery] = None,
        vault_profile_id: int,
        start_time: int = None,
        end_time: int = None,
    ) -> MultipleResponse:
        request_params = dict(pagination)
        if vault_profile_id:
            request_params["vault_profile_id"] = vault_profile_id
        if start_time:
            request_params["start_time"] = (
                start_time * 1000000
            )  # convert to microseconds
        if end_time:
            request_params["end_time"] = end_time * 1000000  # convert to microseconds

        response = await self.transport.get(
            "/vaults/funding",
            params=request_params,
        )
        response.raise_for_status()

        def next_page_func(pagination: PaginationQuery) -> MultipleResponse:
            return self.funding(pagination=pagination)

        return multiple_or_fail(response.json(), next_page_func)

    funding.__doc__ = Vaults.funding.__doc__
