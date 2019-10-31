from cfn_kong_provider import KongProvider

request_schema = {
    "type": "object",
    "required": ["AdminURL", "PluginName", "Credential"],
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
        "PluginName": {
            "type": "string",
            "description": "name of the plugin the credentials below too, key-auth, etc."
        },
        "Credential": {
            "type": "object",
            "required": ["consumer"],
            "properties": {
                "consumer": {
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


class KongCredentialProvider(KongProvider):

    def __init__(self):
        super(KongCredentialProvider, self).__init__('consumers/%(consumer.id)s/%(PluginName)s', 'Credential')
        self.request_schema = request_schema

    @property
    def resource_url(self):
        creds = self.get('Credential')
        return '%s/consumers/%s/%s' % (self.get('AdminURL'), creds.get('consumer',{}).get('id'), self.get('PluginName'))

provider = KongCredentialProvider()


def handler(request, context):
    return provider.handle(request, context)
