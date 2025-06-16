from .transport import Transport, SyncTransport, AsyncTransport
from .signer import JWTTokenSigner, EIP712Signer
from .response import SingleResponse, MultipleResponse, single_or_fail, multiple_or_fail


class Account:
    """
    Account class.

    This class is a wrapper around the RabbitX account API.

    Attributes
    ----------
    transport : Transport
        The transport object
    """

    def __init__(self, transport: Transport):
        self.transport = transport

    def onboarding(self):
        """
        Onboard a new user or login an existing user

        :return: The onboarding result
        :rtype: SingleResponse

        Response:

        .. code-block:: python

            {
                "profile": {
                    "id": 88889,
                    "profile_type": "trader",
                    "status": "active",
                    "wallet": "0x2b0f80b047c63052288e56b9e6ad9d2a4196441f",
                    "last_update": 1748766224507855,
                    "balance": "13665.642201",
                    "account_equity": "13665.642301",
                    "total_position_margin": "0.530005",
                    "total_order_margin": "0.53",
                    "total_notional": "10.6001",
                    "account_margin": "1289.1993755719285667",
                    "withdrawable_balance": "13664.582196",
                    "cum_unrealized_pnl": "0.0001",
                    "health": "1",
                    "account_leverage": "0.000775675212809",
                    "cum_trading_volume": "917.4503",
                    "leverage": {
                        "BTC-USD": "20",
                        "ETH-USD": "20",
                        "SOL-USD": "20"
                    },
                    "last_liq_check": 0,
                    "mmf_total": "0.2650025",
                    "acmf_total": "0.13250125",
                    "positions": [
                        {
                            "id": "pos-BTC-USD-tr-88889",
                            "market_id": "BTC-USD",
                            "profile_id": 88889,
                            "size": "0.0001",
                            "side": "long",
                            "entry_price": "106000",
                            "unrealized_pnl": "0.0001",
                            "notional": "10.6001",
                            "margin": "0.530005",
                            "liquidation_price": "0",
                            "fair_price": "106001"
                        }
                    ],
                    "orders": [
                        {
                            "id": "BTC-USD@1185",
                            "profile_id": 88889,
                            "market_id": "BTC-USD",
                            "order_type": "limit",
                            "status": "open",
                            "price": "106000",
                            "size": "0.0001",
                            "initial_size": "0.0001",
                            "total_filled_size": "0",
                            "side": "long",
                            "timestamp": 1748766209245711,
                            "reason": "",
                            "client_order_id": "",
                            "trigger_price": "0",
                            "size_percent": "0",
                            "time_in_force": "good_till_cancel",
                            "created_at": 1748766209245711,
                            "updated_at": 1748766209245711
                        }
                    ]
                },
                "jwt": "new_jwt_token",
                "refreshToken": "new_refresh_token",
                "randomSecret": "new_random_secret"
            }
        """

        wallet = self.transport.signer.wallet
        headers = self.transport.signer.headers("POST", "/onboarding", None)
        signature = headers["RBT-PK-SIGNATURE"]

        request = {
            "is_client": True,
            "wallet": wallet,
            "profile_type": "trader",
            "signature": signature,
        }

        response = self.transport.post("/onboarding", body=request, headers=headers)
        response.raise_for_status()
        result = single_or_fail(response.json())

        data = result.result()
        jwt_token = data["jwt"]
        refresh_token = data["refreshToken"]
        random_secret = data["randomSecret"]

        self.transport.signer = JWTTokenSigner(jwt_token, refresh_token, random_secret)

        return result

    def renew_jwt_token(self):
        """
        Renew the JWT token.

        It replaces the current signer with a new one if the signer is a JWTTokenSigner or EIP712Signer.

        :return: The new JWT token
        :rtype: SingleResponse

        Response:

        .. code-block:: python

            {
                "jwt": "new_jwt_token"
            }
        """

        is_client = isinstance(self.transport.signer, JWTTokenSigner) or isinstance(
            self.transport.signer, EIP712Signer
        )

        body = {"is_client": is_client}

        if is_client:
            body["refresh_token"] = self.transport.signer.refresh_token

        response = self.transport.post("/jwt", body=body)
        response.raise_for_status()
        result = single_or_fail(response.json())
        data = result.result()  

        if is_client:
            self.transport.signer = JWTTokenSigner(
                data["jwt"], data["refresh_token"], data["random_secret"]
            )

        return result

    def positions(self):
        """
        Get all positions

        :return: The positions
        :rtype: MultipleResponse

        Response:

        .. code-block:: python

            [
                {
                    "id": "pos-BTC-USD-tr-88889",
                    "market_id": "BTC-USD",
                    "profile_id": 88889,
                    "size": "0.0001",
                    "side": "long",
                    "entry_price": "106000",
                    "unrealized_pnl": "0",
                    "notional": "10.6",
                    "margin": "0.53",
                    "liquidation_price": "0",
                    "fair_price": "106000"
                }
            ]
        """

        response = self.transport.get("/positions")
        response.raise_for_status()

        return multiple_or_fail(response.json())


class AsyncAccount:
    __doc__ = Account.__doc__

    def __init__(self, transport: AsyncTransport):
        self.transport = transport

    async def onboarding(self):
        wallet = self.transport.signer.wallet
        headers = self.transport.signer.headers("POST", "/onboarding", None)
        signature = headers["RBT-PK-SIGNATURE"]

        request = {
            "is_client": True,
            "wallet": wallet,
            "profile_type": "trader",
            "signature": signature,
        }

        response = await self.transport.post("/onboarding", body=request, headers=headers)
        response.raise_for_status()
        result = single_or_fail(response.json())
        
        data = result.result()
        jwt_token = data["jwt"]
        refresh_token = data["refreshToken"]
        random_secret = data["randomSecret"]

        self.transport.signer = JWTTokenSigner(jwt_token, refresh_token, random_secret)

        return result
    
    onboarding.__doc__ = Account.onboarding.__doc__

    async def renew_jwt_token(self):
        is_client = isinstance(self.transport.signer, JWTTokenSigner) or isinstance(
            self.transport.signer, EIP712Signer
        )

        body = {"is_client": is_client}

        if is_client:
            body["refresh_token"] = self.transport.signer.refresh_token

        response = await self.transport.post("/jwt", body=body)
        response.raise_for_status()
        result = single_or_fail(response.json())
        data = result.result()

        if is_client:
            self.transport.signer = JWTTokenSigner(
                data["jwt"], data["refresh_token"], data["random_secret"]
            )

        return result
    
    renew_jwt_token.__doc__ = Account.renew_jwt_token.__doc__

    async def positions(self):
        response = await self.transport.get("/positions")
        response.raise_for_status()
        return multiple_or_fail(response.json())
    
    positions.__doc__ = Account.positions.__doc__
