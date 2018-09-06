from cfn_kong_provider import KongProvider

request_schema = {
    "type": "object",
    "required": ["AdminURL", "Service"],
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
        "Service": {
            "type": "object",
            "required": ["host"],
            "properties": {
                "name": {
                    "type": "string"
                },
                "protocol": {
                    "type": "string", "default": "http", "enum": ["http", "https"]
                },
                "host": {
                    "type": "string"
                },
                "port": {
                    "type": "integer", "default": 80
                },
                "path": {
                    "type": "string"
                },
                "retries": {
                    "type": "integer", "default": 5
                },
                "connect_timeout": {
                    "type": "integer", "default": 60000
                },
                "write_timeout": {
                    "type": "integer", "default": 60000
                },
                "read_timeout": {
                    "type": "integer", "default": 60000
                }
            }
        }
    }
}


class KongServiceProvider(KongProvider):

    def __init__(self):
        super(KongServiceProvider, self).__init__('services', 'Service')
        self.request_schema = request_schema


provider = KongServiceProvider()


def handler(request, context):
    return provider.handle(request, context)
