import json

class ApiKey:
    """
    ApiKey class.

    This class is used to store the API key and secret.

    Attributes
    ----------
    key : str
        The API key
    secret : str
        The API secret
    public_jwt : str
        The public JWT
    private_jwt : str
        The private JWT
    """

    def __init__(self, key, secret, public_jwt, private_jwt):
        self.key = key
        self.secret = secret
        self.public_jwt = public_jwt
        self.private_jwt = private_jwt

    def __str__(self):
        return self.key

def read_from_json_file(path:str) -> ApiKey:
    """
    Read the API key and secret from a JSON file.

    :param path: The path to the JSON file
    :type path: str
    :return: The ApiKey object
    """
    with open(path, 'r') as f:
        data = json.load(f)
        return ApiKey(data['key'], data['secret'], data['publicJwt'], data['privateJwt'])

def new_api_key(key:str, secret:str, public_jwt:str="", private_jwt:str="") -> ApiKey:
    """
    Create a new ApiKey object.

    :param key: The API key
    :type key: str
    :param secret: The API secret
    :type secret: str
    :param public_jwt: The public JWT
    :type public_jwt: str
    :param private_jwt: The private JWT
    :type private_jwt: str
    :return: The ApiKey object
    :rtype: ApiKey
    """
    return ApiKey(key, secret, public_jwt, private_jwt)