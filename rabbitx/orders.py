from typing import TypedDict, Literal, Optional

from rabbitx.private_request import private_api_request
from apikey import ApiKey

OrderSide = Literal["long", "short"]
OrderType = Literal["limit", "market"] # Add more types later here


class CreateOrderParams(TypedDict):
    market_id: str
    type: OrderType
    side: OrderSide
    price: float
    size: float
    # trigger_price: Optional[float] 
    # time_in_force: Optional[str]

def create_order(tg_id:str, order_params:CreateOrderParams):
    """Create an order with the given parameters.
    
    Args:
        jwt: Authentication token
        order_params: Dictionary containing :
            - market_id: Market identifier
            - type: Order type ('limit' or 'market')
            - side: Side of trade ('long' or 'short')
            - price: Order price
            - size: Order size
            - trigger_price: Optional trigger price
            - time_in_force: Optional time in force parameter
    """
    
    response = rabbit_private_requestion(
        tg_id=tg_id,
        endpoint="/orders",
        method='post',
        json=order_params,
    )
    
    if response.status_code >= 200 and response.status_code < 300:
        return response.json()
    
    print(response.text)
    
    return None

def get_orders(apiKey: ApiKey):   
    response = private_api_request(
        apiKey,
        method='get',
        endpoint="/orders",
    )
    
    print(response.text)
    
    return response.json()