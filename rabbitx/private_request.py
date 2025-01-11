from typing import Literal
import requests

from config import BASE_URL
from rabbitx.utils import create_headers, new_payload, payload_hash, rbt_signature
from utils.time import get_current_timestamp
from apikey import ApiKey

def private_api_request(apiKey: ApiKey, method = 'get', endpoint:str = '', json = {}, headers = {}):
    timestamp = get_current_timestamp()+15
    
    payload = new_payload(method.upper(), endpoint, params=json)
    hashed_payload = payload_hash(timestamp, payload)
    signature = rbt_signature(hashed_payload, apiKey.secret)
    headers.update({
        "RBT-TS": str(timestamp),
        'RBT-API-KEY': apiKey.key,
        "RBT-SIGNATURE": signature,
    })

    response = requests.request(method, json=json, url=f"{BASE_URL}{endpoint}", headers=headers)
    
    return response

'''
def rabbit_private_requestion(tg_id, method: Literal['post', 'get'], endpoint:str = '', json = {}, ):
    # Fetch customer from the database based on tg_id
    try:
        customer = db.get_customer(tg_id)
        
        if not customer :
            return {"success": False, "message": "You don't have an account yet. Please use /start to create an account."}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "message": "You don't have an account yet. Please use /start to create an account."}
    
    
    random_secret = customer['random_secret']
    jwt = customer['jwt']
    
    cookies = {
        'jwt': jwt,
    }
    
    timestamp = get_current_timestamp()+15
    
    payload = new_payload(method.upper(), endpoint, params=json)
    hashed_payload = payload_hash(timestamp, payload)
    signature = rbt_signature(hashed_payload, random_secret)
    headers = create_headers(timestamp, signature, jwt)
    
    # Call the normal request with the passed in info, jwt, and signature
    response = requests.request(method, json=json, cookies=cookies, url=f"{BASE_URL}{endpoint}", headers=headers)
    
    return response
'''