from cfn_kong_provider import KongProvider

request_schema = {
    "type": "object",
    "required": ["AdminURL", "Route"],
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
        "Route": {
            "type": "object",
            "required": ["service"],
            "properties": {
                "protocols": {
                    "type": "array",
                    "items": {
                        "type": "string", "enum": [ "http", "https"]
                    }
                },
                "methods": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "hosts": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "paths": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "strip_path": {
                    "type": "boolean", "default": True
                },
                "preserve_host": {
                    "type": "boolean", "default": False
                },
                "service": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {
                            "type": "string"
                        }
                    }

                }
            }
        }
    }
}


class KongRouteProvider(KongProvider):

    def __init__(self):
        super(KongRouteProvider, self).__init__('routes', 'Route')
        self.request_schema = request_schema


provider = KongRouteProvider()


def handler(request, context):
    return provider.handle(request, context)
