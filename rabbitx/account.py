from rabbitx.client import Client
from rabbitx.signer import JWTTokenSigner, EIP712Signer


class Account:
    """
    Account class.

    This class is a wrapper around the RabbitX account API.

    Attributes
    ----------
    client : Client
        The client object
    """

    def __init__(self, client: Client):
        self.client = client

    def onboarding(self):
        """
        Onboard a new user or login an existing user

        :return: The onboarding result
        :rtype: dict

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

        wallet = self.client.signer.wallet
        headers = self.client.signer.headers("POST", "/onboarding", None)
        signature = headers["RBT-PK-SIGNATURE"]

        request = {
            "is_client": True,
            "wallet": wallet,
            "profile_type": "trader",
            "signature": signature,
        }

        response = self.client.post("/onboarding", body=request, headers=headers)
        response.raise_for_status()
        result = response.json()

        jwt_token = result["result"][0]["jwt"]
        refresh_token = result["result"][0]["refreshToken"]
        random_secret = result["result"][0]["randomSecret"]

        self.client.signer = JWTTokenSigner(jwt_token, refresh_token, random_secret)

        return result["result"][0]

    def renew_jwt_token(self):
        """
        Renew the JWT token.

        It replaces the current signer with a new one if the signer is a JWTTokenSigner or EIP712Signer.

        :return: The new JWT token
        :rtype: dict

        Response:

        .. code-block:: python

            {
                "jwt": "new_jwt_token"
            }
        """

        is_client = isinstance(self.client.signer, JWTTokenSigner) or isinstance(
            self.client.signer, EIP712Signer
        )

        body = {"is_client": is_client}

        if is_client:
            body["refresh_token"] = self.client.signer.refresh_token

        response = self.client.post("/jwt", body=body)
        response.raise_for_status()
        result = response.json()["result"][0]

        if is_client:
            self.client.signer = JWTTokenSigner(
                result["jwt"], result["refresh_token"], result["random_secret"]
            )

        return {"jwt": result["jwt"]}

    def positions(self):
        """
        Get all positions

        :return: The positions
        :rtype: list

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

        response = self.client.get("/positions")
        response.raise_for_status()
        result = response.json()

        return result["result"]
