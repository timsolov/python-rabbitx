import os
from typing import Optional
from pydantic import BaseModel

SHOW_REQUEST_ID = os.getenv("SHOW_REQUEST_ID") or False


class UnsuccessfulResponse(Exception):
    pass


class BadResult(Exception):
    pass


class APIResponse(BaseModel):
    success: bool
    result: Optional[list[dict | bool]] = None
    request_id: Optional[str] = None
    pagination: Optional[dict] = None


class SingleResponse:
    def __init__(self, response: APIResponse):
        self.response = response

    def result(self) -> dict:
        return self.response.result[0]


class MultipleResponse:
    def __init__(self, response: APIResponse):
        self.response = response

    def result(self) -> list:
        return self.response.result


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


def multiple_or_fail(response) -> MultipleResponse:
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

    return MultipleResponse(response)
