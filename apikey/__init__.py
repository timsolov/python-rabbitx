class ApiKey:
    def __init__(self, key, secret, public_jwt, private_jwt):
        self.key = key
        self.secret = secret
        self.public_jwt = public_jwt
        self.private_jwt = private_jwt

    def __str__(self):
        return self.key