import pytest
from unittest.mock import MagicMock, AsyncMock
from decimal import Decimal
from rabbitx.orders import Orders, AsyncOrders, CreateOrderParams


@pytest.fixture
def mock_transport():
    transport = MagicMock()
    transport.post.return_value.json.return_value = {
        "success": True,
        "result": [{"status": "processing"}],
    }
    transport.post.return_value.raise_for_status.return_value = None
    transport.get.return_value.json.return_value = {"success": True, "result": []}
    transport.get.return_value.raise_for_status.return_value = None
    transport.put.return_value.json.return_value = {
        "success": True,
        "result": [{"status": "amending"}],
    }
    transport.put.return_value.raise_for_status.return_value = None
    transport.delete.return_value.json.return_value = {
        "success": True,
        "result": [{"status": "canceling"}],
    }
    transport.delete.return_value.raise_for_status.return_value = None
    return transport


@pytest.fixture
def mock_async_transport():
    transport = AsyncMock()

    # POST
    post_response = AsyncMock()
    post_response.json = MagicMock(
        return_value={"success": True, "result": [{"status": "processing"}]}
    )
    post_response.raise_for_status = MagicMock()
    transport.post.return_value = post_response

    # GET
    get_response = AsyncMock()
    get_response.json = MagicMock(return_value={"success": True, "result": []})
    get_response.raise_for_status = MagicMock()
    transport.get.return_value = get_response

    # PUT
    put_response = AsyncMock()
    put_response.json = MagicMock(
        return_value={"success": True, "result": [{"status": "amending"}]}
    )
    put_response.raise_for_status = MagicMock()
    transport.put.return_value = put_response

    # DELETE
    delete_response = AsyncMock()
    delete_response.json = MagicMock(
        return_value={"success": True, "result": [{"status": "canceling"}]}
    )
    delete_response.raise_for_status = MagicMock()
    transport.delete.return_value = delete_response

    return transport


@pytest.fixture
def orders(mock_transport):
    return Orders(mock_transport)


@pytest.fixture
def async_orders(mock_async_transport):
    return AsyncOrders(mock_async_transport)


class TestOrders:
    def test_create_order(self, orders: Orders, mock_transport: MagicMock):
        params: CreateOrderParams = {
            "market_id": "BTC-USD",
            "type": "limit",
            "side": "long",
            "price": "10000.0",
            "size": "1.0",
        }
        orders.create(**params)
        mock_transport.post.assert_called_once()
        args, kwargs = mock_transport.post.call_args
        assert args[0] == "/orders"
        assert kwargs["body"]["price"] == 10000.0

    def test_list_orders(self, orders: Orders, mock_transport: MagicMock):
        orders.list(market_id="BTC-USD")
        mock_transport.get.assert_called_once_with(
            "/orders", params={"market_id": "BTC-USD"}
        )

    def test_list_orders_with_pagination(
        self, orders: Orders, mock_transport: MagicMock
    ):
        first_page_response = {
            "success": True,
            "result": [{"id": "1"}],
            "pagination": {
                "page": 1,
                "limit": 1,
                "has_next_page": True,
                "order": "DESC",
            },
        }
        second_page_response = {
            "success": True,
            "result": [{"id": "2"}],
            "pagination": {
                "page": 2,
                "limit": 1,
                "has_next_page": False,
                "order": "DESC",
            },
        }

        resp1 = MagicMock()
        resp1.json.return_value = first_page_response
        resp1.raise_for_status.return_value = None

        resp2 = MagicMock()
        resp2.json.return_value = second_page_response
        resp2.raise_for_status.return_value = None

        mock_transport.get.side_effect = [resp1, resp2]

        response = orders.list(market_id="BTC-USD")

        assert response.has_next_page is True
        assert response.result()[0]["id"] == "1"

        next_page_response = response.next_page()

        assert next_page_response.has_next_page is False
        assert next_page_response.result()[0]["id"] == "2"

        assert mock_transport.get.call_count == 2

        _, call_one_kwargs = mock_transport.get.call_args_list[0]
        assert call_one_kwargs["params"] == {"market_id": "BTC-USD"}

        _, call_two_kwargs = mock_transport.get.call_args_list[1]
        assert call_two_kwargs["params"] == {
            "market_id": "BTC-USD",
            "p_page": 2,
            "p_limit": 1,
            "p_order": "DESC",
        }

    def test_amend_order(self, orders: Orders, mock_transport: MagicMock):
        params = {
            "order_id": "123",
            "market_id": "BTC-USD",
            "price": Decimal("11000.0"),
        }
        orders.amend(**params)
        mock_transport.put.assert_called_once()
        args, kwargs = mock_transport.put.call_args
        assert args[0] == "/orders"
        assert kwargs["body"]["price"] == 11000.0

    def test_cancel_order(self, orders: Orders, mock_transport: MagicMock):
        params = {"order_id": "123", "market_id": "BTC-USD"}
        orders.cancel(**params)
        mock_transport.delete.assert_called_once_with("/orders", body=params)

    def test_cancel_all_orders(self, orders: Orders, mock_transport: MagicMock):
        mock_transport.delete.return_value.json.return_value = {
            "success": True,
            "result": [True],
        }
        orders.cancel_all()
        mock_transport.delete.assert_called_once_with("/orders/cancel_all", body={})


@pytest.mark.asyncio
class TestAsyncOrders:
    async def test_create_order(
        self, async_orders: AsyncOrders, mock_async_transport: AsyncMock
    ):
        params: CreateOrderParams = {
            "market_id": "BTC-USD",
            "type": "limit",
            "side": "long",
            "price": "10000.0",
            "size": "1.0",
        }
        await async_orders.create(**params)
        mock_async_transport.post.assert_called_once()
        args, kwargs = mock_async_transport.post.call_args
        assert args[0] == "/orders"
        assert kwargs["body"]["price"] == 10000.0

    async def test_list_orders(
        self, async_orders: AsyncOrders, mock_async_transport: AsyncMock
    ):
        await async_orders.list(market_id="BTC-USD")
        mock_async_transport.get.assert_called_once_with(
            "/orders", params={"market_id": "BTC-USD"}
        )

    async def test_list_orders_with_pagination(
        self, async_orders: AsyncOrders, mock_async_transport: AsyncMock
    ):
        first_page_response = {
            "success": True,
            "result": [{"id": "1"}],
            "pagination": {
                "page": 1,
                "limit": 1,
                "has_next_page": True,
                "order": "DESC",
            },
        }
        second_page_response = {
            "success": True,
            "result": [{"id": "2"}],
            "pagination": {
                "page": 2,
                "limit": 1,
                "has_next_page": False,
                "order": "DESC",
            },
        }

        resp1 = AsyncMock()
        resp1.json = MagicMock(return_value=first_page_response)
        resp1.raise_for_status = MagicMock()

        resp2 = AsyncMock()
        resp2.json = MagicMock(return_value=second_page_response)
        resp2.raise_for_status = MagicMock()

        mock_async_transport.get.side_effect = [resp1, resp2]

        response = await async_orders.list(market_id="BTC-USD")

        assert response.has_next_page is True
        assert response.result()[0]["id"] == "1"

        next_page_response = await response.next_page()

        assert next_page_response.has_next_page is False
        assert next_page_response.result()[0]["id"] == "2"

        assert mock_async_transport.get.call_count == 2

        _, call_one_kwargs = mock_async_transport.get.call_args_list[0]
        assert call_one_kwargs["params"] == {"market_id": "BTC-USD"}

        _, call_two_kwargs = mock_async_transport.get.call_args_list[1]
        assert call_two_kwargs["params"] == {
            "market_id": "BTC-USD",
            "p_page": 2,
            "p_limit": 1,
            "p_order": "DESC",
        }

    async def test_amend_order(
        self, async_orders: AsyncOrders, mock_async_transport: AsyncMock
    ):
        params = {
            "order_id": "123",
            "market_id": "BTC-USD",
            "price": Decimal("11000.0"),
        }
        await async_orders.amend(**params)
        mock_async_transport.put.assert_called_once()
        args, kwargs = mock_async_transport.put.call_args
        assert args[0] == "/orders"
        assert kwargs["body"]["price"] == 11000.0

    async def test_cancel_order(
        self, async_orders: AsyncOrders, mock_async_transport: AsyncMock
    ):
        params = {"order_id": "123", "market_id": "BTC-USD"}
        await async_orders.cancel(**params)
        mock_async_transport.delete.assert_called_once_with("/orders", body=params)

    async def test_cancel_all_orders(
        self, async_orders: AsyncOrders, mock_async_transport: AsyncMock
    ):
        delete_response = AsyncMock()
        delete_response.json = MagicMock(
            return_value={"success": True, "result": [True]}
        )
        delete_response.raise_for_status = MagicMock()
        mock_async_transport.delete.return_value = delete_response

        await async_orders.cancel_all()
        mock_async_transport.delete.assert_called_once_with(
            "/orders/cancel_all", body={}
        )
