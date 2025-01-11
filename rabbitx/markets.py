import requests

from rabbitx.rabbitx import BASE_URL
from rabbitx.private_request import rabbit_private_requestion


def get_markets_ids():
    response = requests.get(
        f"{BASE_URL}/markets",
    )
    return [i['id'] for i in response.json()['result']]

def tokens():
    response = requests.get(
        f"{BASE_URL}/markets",
    )
    return [i['id'].replace("-USD", "") for i in response.json()['result']]


def markets(tg_id):
    response = rabbit_private_requestion(
        tg_id=tg_id,
        endpoint="/markets",
        method='get',
    )
    
    if response.status_code == 200:
        return response.json()
    
    return None

