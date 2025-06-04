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

    @staticmethod
    def from_file(path: str) -> "ApiKey":
        """
        Read the API key and secret from a JSON file.

        :param path: The path to the JSON file
        :type path: str
        :return: The ApiKey object
        :rtype: ApiKey

        Example:

        .. code-block:: python

            from rabbitx.apikey import ApiKey
            api_key = ApiKey.from_json_file('.apikey/apiKey.json')
            print(api_key)
        """
        with open(path, "r") as f:
            data = json.load(f)
            return ApiKey(
                data["key"], data["secret"], data["publicJwt"], data["privateJwt"]
            )
