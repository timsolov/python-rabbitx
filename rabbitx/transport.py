from rabbitx.signer import Signer
import requests
import json
import os
import urllib3
from decimal import Decimal
import logging

urllib3.disable_warnings()

DEBUG = os.getenv("DEBUG", False)

if DEBUG:
    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig(level=logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

logger = logging.getLogger("rabbitx.transport")


class CustomEncoder(json.JSONEncoder):
    """
    Custom encoder for the JSON library.

    This class is used to encode Decimal and bool objects to strings the right way.
    """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, bool):
            return str(obj).lower()
        return super().default(obj)


class Transport:
    """
    Transport class.

    This class is a wrapper around the RabbitX transport.

    Attributes
    ----------
    base_url : str
        The base URL of the RabbitX API
    signer : Signer
        The signer object
    headers : dict
        The headers to send with the request
    """

    def __init__(self, base_url: str, signer: Signer, headers={}):
        self.base_url = base_url
        self.signer = signer
        self.client = requests.Session()
        self.headers = headers

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict = {},
        body: dict = {},
        headers: dict = {},
    ):
        self.client.headers = self.signer.headers(method, endpoint, body)
        self.client.headers.update(self.headers)
        self.client.headers.update(headers)

        body = json.dumps(body, indent=2, cls=CustomEncoder)

        response = self.client.request(
            method,
            data=body,
            url=f"{self.base_url}{endpoint}",
            params=params,
            verify=False,
        )

        if DEBUG:
            logger.debug(f"Response: {response.text}")

        return response

    def get(self, endpoint: str, params={}):
        return self._request("GET", endpoint=endpoint, params=params)

    def post(self, endpoint: str, body={}, headers={}):
        return self._request("POST", endpoint=endpoint, body=body)

    def put(self, endpoint: str, body={}):
        return self._request("PUT", endpoint=endpoint, body=body)

    def delete(self, endpoint: str, body={}):
        return self._request("DELETE", endpoint=endpoint, body=body)
