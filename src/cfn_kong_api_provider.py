from cfn_kong_provider import KongProvider

request_schema = {
    "type": "object",
    "required": ["AdminURL"],
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
        "API": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {
                    "type": "string"
                },
                "upstream_url": {
                    "type": "string", "pattern": "https?://.+"
                },
                "hosts": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "uris": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "http_if_terminated": {
                    "type": "boolean", "default": True
                },
                "https_only": {
                    "type": "boolean", "default": False
                },
                "strip_uri": {
                    "type": "boolean", "default": False
                },
                "preserve_host": {
                    "type": "boolean", "default": False
                },
                "retries": {
                    "type": "integer", "default": 5
                },
                "upstream_connect_timeout": {
                    "type": "integer", "default": 60000
                },
                "upstream_send_timeout": {
                    "type": "integer", "default": 60000
                },
                "upstream_read_timeout": {
                    "type": "integer", "default": 60000
                }
            }
        }
    }
}


class KongAPIProvider(KongProvider):

    def __init__(self):
        super(KongAPIProvider, self).__init__('apis', 'API')
        self.request_schema = request_schema

provider = KongAPIProvider()


def handler(request, context):
    return provider.handle(request, context)
