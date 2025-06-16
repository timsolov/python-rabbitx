import pytest
from rabbitx.response import (
    single_or_fail,
    multiple_or_fail,
    UnsuccessfulResponse,
    BadResult,
)
from pydantic import ValidationError


# --- single_or_fail tests ---
def test_single_or_fail_success():
    response = {
        "success": True,
        "result": [{"foo": "bar"}],
        "request_id": "abc123",
        "pagination": None,
    }
    single = single_or_fail(response)
    assert single.result() == {"foo": "bar"}


def test_single_or_fail_unsuccessful():
    response = {
        "success": False,
        "result": [{"foo": "bar"}],
        "request_id": None,
        "pagination": None,
    }
    with pytest.raises(UnsuccessfulResponse):
        single_or_fail(response)


def test_single_or_fail_no_result():
    response = {"success": True, "result": [], "request_id": None, "pagination": None}
    with pytest.raises(BadResult):
        single_or_fail(response)


def test_single_or_fail_multiple_results():
    response = {
        "success": True,
        "result": [{"foo": 1}, {"foo": 2}],
        "request_id": None,
        "pagination": None,
    }
    with pytest.raises(BadResult):
        single_or_fail(response)


def test_single_or_fail__success_field_invalid():
    response = {
        "success": 123,
        "result": [{"foo": 1}],
        "request_id": "abc123",
        "pagination": None,
    }
    with pytest.raises(ValidationError):
        single_or_fail(response)


# --- multiple_or_fail tests ---
def test_multiple_or_fail_success():
    response = {
        "success": True,
        "result": [{"foo": 1}, {"foo": 2}],
        "request_id": "abc123",
        "pagination": None,
    }
    multiple = multiple_or_fail(response)
    assert multiple.result() == [{"foo": 1}, {"foo": 2}]


def test_multiple_or_fail_unsuccessful():
    response = {
        "success": False,
        "result": [{"foo": 1}, {"foo": 2}],
        "request_id": None,
        "pagination": None,
    }
    with pytest.raises(UnsuccessfulResponse):
        multiple_or_fail(response)


def test_multiple_or_fail_no_result():
    response = {"success": True, "result": [], "request_id": None, "pagination": None}
    with pytest.raises(BadResult):
        multiple_or_fail(response)
