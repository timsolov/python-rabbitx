from rabbitx.private_request import private_api_request
from apikey import ApiKey

def get_vaults(apiKey: ApiKey):   
    response = private_api_request(
        apiKey,
        method='get',
        endpoint="/vaults",
        headers={"EID": "rbx"},
    )
    
    print(response.text)
    
    return response.json()