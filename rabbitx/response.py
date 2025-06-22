import os
from typing import Optional, Union, List, Callable
from pydantic import BaseModel
from .request import PaginationQuery

SHOW_REQUEST_ID = os.getenv("SHOW_REQUEST_ID") or False


class UnsuccessfulResponse(Exception):
    pass


class BadResult(Exception):
    pass


class NoNextPage(Exception):
    pass


class Pagination(BaseModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[str] = None
    has_next_page: Optional[bool] = False


class APIResponse(BaseModel):
    success: bool
    result: Optional[List[Union[dict, bool]]] = None
    request_id: Optional[str] = None
    pagination: Optional[Pagination] = None


class SingleResponse:
    def __init__(self, response: APIResponse):
        self.response = response

    def result(self) -> dict:
        """
        Returns the single result.
        """
        return self.response.result[0]


class MultipleResponse:
    """
    MultipleResponse class.

    This class is a wrapper around the RabbitX multiple response API.

    Attributes
    ----------
    response : APIResponse
        The response object

    Example:
    .. code-block:: python

        response = rabbitx.orders.list(
            market_id="BTC-USD",
            status=["open"],
        )

        print(response.result())

        while response.has_next_page:
            response = response.next_page()
            print(response.result())
    """

    def __init__(
        self,
        response: APIResponse,
        next_page_func: Callable[[PaginationQuery], "MultipleResponse"],
    ):
        self.response = response
        self.next_page_func = next_page_func

    def result(self) -> list:
        """
        Returns the list of results.
        """
        return self.response.result

    @property
    def has_next_page(self) -> bool:
        """
        Returns True if there is a next page of results.
        """
        return (
            self.response.pagination and self.response.pagination.has_next_page
        ) or False

    def next_page(self) -> "MultipleResponse":
        """
        Returns a MultipleResponse object with the next page of results.

        raises:
            NoNextPage: if there is no next page
        """
        if not self.has_next_page:
            raise NoNextPage()

        pagination = PaginationQuery(
            p_page=self.response.pagination.page + 1 if self.response.pagination else 1,
            p_limit=self.response.pagination.limit if self.response.pagination else 50,
            p_order=self.response.pagination.order
            if self.response.pagination
            else "DESC",
        )

        return self.next_page_func(pagination)


def single_or_fail(response) -> SingleResponse:
    """
    Returns a SingleResponse object if the response is successful and has a single result.

    raises:
        UnsuccessfulResponse: if the response is not successful
        BadResult: if the response has no results or multiple results
        pydantic.ValidationError: if the response is not a valid APIResponse
    """
    response = APIResponse.model_validate(response)

    if SHOW_REQUEST_ID and response.request_id:
        print(f"Request ID: {response.request_id}")

    if not response.success:
        raise UnsuccessfulResponse(response)

    if not response.result:
        raise BadResult(response)

    if len(response.result) == 0:
        raise BadResult("expected 1 result, got 0")

    if len(response.result) > 1:
        raise BadResult("expected 1 result, got multiple")

    return SingleResponse(response)


def multiple_or_fail(
    response,
    next_page_func: Union[Callable[[PaginationQuery], MultipleResponse], None] = None,
) -> MultipleResponse:
    """
    Returns a MultipleResponses object if the response is successful and has multiple results.

    raises:
        UnsuccessfulResponse: if the response is not successful
        BadResult: if the response has no result key in the response
        pydantic.ValidationError: if the response is not a valid APIResponse
    """
    response = APIResponse.model_validate(response)

    if SHOW_REQUEST_ID and response.request_id:
        print(f"Request ID: {response.request_id}")

    if not response.success:
        raise UnsuccessfulResponse(response)

    if response.result is None:
        raise BadResult(response)

    return MultipleResponse(response, next_page_func)


def collect_pages(response: MultipleResponse) -> list:
    """
    Helper function to collect all the pages from a MultipleResponse object.

    Example:
    .. code-block:: python

        response = rabbitx.orders.list(
            market_id="BTC-USD",
            status=["open"],
        )

        for order in collect_pages(response):
            print(order)
    """
    results = response.result()
    while response.has_next_page:
        response = response.next_page()
        results.extend(response.result())
    return results


async def collect_pages_async(response: MultipleResponse) -> list:
    """
    Helper function to collect all the pages from a MultipleResponse object.

    Async version of collect_pages.

    Example:
    .. code-block:: python

        response = rabbitx.orders.list(
            market_id="BTC-USD",
            status=["open"],
        )

        for order in await collect_pages_async(response):
            print(order)
    """
    results = response.result()
    while response.has_next_page:
        response = await response.next_page()
        results.extend(response.result())
    return results
