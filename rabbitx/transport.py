from rabbitx.signer import Signer
import json
import os
from decimal import Decimal
import logging
import httpx
from abc import ABC, abstractmethod

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


class Transport(ABC):
    """
    Abstract base class for RabbitX transport.

    This class defines the interface for both synchronous and asynchronous transports.

    Attributes
    ----------
    base_url : str
        The base URL of the RabbitX API
    signer : Signer
        The signer object
    headers : dict
        The headers to send with the request
    """

    def __init__(self, base_url: str, signer: Signer, headers: dict = {}):
        self.base_url = base_url
        self.signer = signer
        self.headers = headers

    @abstractmethod
    def get(self, endpoint: str, params: dict = {}):
        """
        Send a GET request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to send the request to
        params : dict, optional
            Query parameters to include in the request, by default {}

        Returns
        -------
        Response
            The response from the API
        """
        pass

    @abstractmethod
    def post(self, endpoint: str, body: dict = {}, headers: dict = {}):
        """
        Send a POST request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to send the request to
        body : dict, optional
            The request body, by default {}
        headers : dict, optional
            Additional headers to include in the request, by default {}

        Returns
        -------
        Response
            The response from the API
        """
        pass

    @abstractmethod
    def put(self, endpoint: str, body: dict = {}):
        """
        Send a PUT request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to send the request to
        body : dict, optional
            The request body, by default {}

        Returns
        -------
        Response
            The response from the API
        """
        pass

    @abstractmethod
    def delete(self, endpoint: str, body: dict = {}):
        """
        Send a DELETE request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to send the request to
        body : dict, optional
            The request body, by default {}

        Returns
        -------
        Response
            The response from the API
        """
        pass


class SyncTransport(Transport):
    """
    Synchronous transport class for RabbitX API using httpx.Client.

    Attributes
    ----------
    base_url : str
        The base URL of the RabbitX API
    signer : Signer
        The signer object
    headers : dict
        The headers to send with the request
    client : httpx.Client
        The underlying HTTP client
    """

    def __init__(self, base_url: str, signer: Signer, headers: dict = {}):
        super().__init__(base_url, signer, headers)
        self.client = httpx.Client(verify=False)

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
        self.client.headers.update({"X-RBT-Client": "desktop"})

        body_json = json.dumps(body, indent=2, cls=CustomEncoder)

        response = self.client.request(
            method,
            url=f"{self.base_url}{endpoint}",
            params=params,
            content=body_json,
            # verify=False,
        )

        if DEBUG:
            logger.debug(f"Response: {response.text}")

        return response

    def get(self, endpoint: str, params: dict = {}):
        return self._request("GET", endpoint=endpoint, params=params)

    def post(self, endpoint: str, body: dict = {}, headers: dict = {}):
        return self._request("POST", endpoint=endpoint, body=body, headers=headers)

    def put(self, endpoint: str, body: dict = {}):
        return self._request("PUT", endpoint=endpoint, body=body)

    def delete(self, endpoint: str, body: dict = {}):
        return self._request("DELETE", endpoint=endpoint, body=body)


class AsyncTransport(Transport):
    """
    Asynchronous transport class for RabbitX API using httpx.AsyncClient.

    Attributes
    ----------
    base_url : str
        The base URL of the RabbitX API
    signer : Signer
        The signer object
    headers : dict
        The headers to send with the request
    client : httpx.AsyncClient
        The underlying async HTTP client
    """

    def __init__(self, base_url: str, signer: Signer, headers: dict = {}):
        super().__init__(base_url, signer, headers)
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(verify=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            self.client = None

    async def _ensure_client(self):
        if not self.client:
            self.client = httpx.AsyncClient(verify=False)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict = {},
        body: dict = {},
        headers: dict = {},
    ):
        await self._ensure_client()
        self.client.headers = self.signer.headers(method, endpoint, body)
        self.client.headers.update(self.headers)
        self.client.headers.update(headers)

        body_json = json.dumps(body, indent=2, cls=CustomEncoder)

        response = await self.client.request(
            method,
            url=f"{self.base_url}{endpoint}",
            params=params,
            content=body_json,
        )

        if DEBUG:
            logger.debug(f"Response: {response.text}")

        return response

    async def get(self, endpoint: str, params: dict = {}):
        return await self._request("GET", endpoint=endpoint, params=params)

    async def post(self, endpoint: str, body: dict = {}, headers: dict = {}):
        return await self._request(
            "POST", endpoint=endpoint, body=body, headers=headers
        )

    async def put(self, endpoint: str, body: dict = {}):
        return await self._request("PUT", endpoint=endpoint, body=body)

    async def delete(self, endpoint: str, body: dict = {}):
        return await self._request("DELETE", endpoint=endpoint, body=body)
