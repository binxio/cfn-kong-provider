from cfn_kong_provider import KongProvider

request_schema = {
    "type": "object",
    "required": ["AdminURL", "Plugin"],
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
        "Plugin": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {
                    "type": "string"
                },
                "consumer_id": {
                    "type": "string"
                },
                "api_id": {
                    "type": "string"
                },
                "config": {
                    "type": "object"
                }
            }
        }
    }
}


class KongPluginProvider(KongProvider):

    def __init__(self):
        super(KongPluginProvider, self).__init__('plugins', 'Plugin')
        self.request_schema = request_schema

provider = KongPluginProvider()


def handler(request, context):
    return provider.handle(request, context)
