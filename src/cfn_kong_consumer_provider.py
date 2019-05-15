from cfn_kong_provider import KongProvider

request_schema = {
    "type": "object",
    "required": ["AdminURL", "Consumer"],
    "properties": {
        "AdminURL":  {
            "type": "string",  "pattern": "^https?://.+",
            "description": "of kong admin port"},
        "JWT": {
            "type": "object",
            "required": ["PrivateKeyParameterName"],
            "properties": {
                    "Issuer": {
                        "type": "string", "default": "admin",
                        "description": "iss attribute of the JWT token"
                    },
                "PrivateKeyParameterName": {
                        "type": "string",
                        "description": "containing the RSA key in PEM encoding to sign the JWT token with"
                        }
            }
        },
        "Consumer": {
            "type": "object",
            "anyOf": [{
                "properties": {
                    "custom_id": {
                        "type": "string"
                    },
                    "username": {
                        "type": "string"
                    }
                },
                "required": ["username"]
            }, {
                "properties": {
                    "custom_id": {
                        "type": "string"
                    },
                    "username": {
                        "type": "string"
                    }
                },
                "required": ["custom_id"]
            }
            ]
        }
    }
}


class KongConsumerProvider(KongProvider):

    def __init__(self):
        super(KongConsumerProvider, self).__init__('consumers', 'Consumer')
        self.request_schema = request_schema

provider = KongConsumerProvider()


def handler(request, context):
    return provider.handle(request, context)
