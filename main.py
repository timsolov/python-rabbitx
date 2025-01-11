import os
import threading
import json
from apikey import ApiKey
from rabbitx.orders import get_orders
from rabbitx.vaults import get_vaults

with open('.vscode/apiKey.json') as f:
    data = json.load(f)
    apiKey = ApiKey(data['key'], data['secret'], data['publicJwt'], data['privateJwt'])
    
# orders = get_orders(apiKey)

vaults = get_vaults(apiKey)