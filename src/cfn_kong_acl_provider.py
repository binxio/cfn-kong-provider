from cfn_kong_provider import KongProvider

request_schema = {
    "type": "object",
    "required": ["AdminURL", "ACL"],
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
        "ACL": {
            "type": "object",
            "required": ["consumer", "group"],
            "properties": {
                "consumer": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "of the consumer"
                        }
                    }
                },
                "group": {
                    "type": "string"
                }
            }
        }
    }
}


class KongACLProvider(KongProvider):

    def __init__(self):
        super(KongACLProvider, self).__init__('consumers/%(consumer.id)s/acls', 'ACL')
        self.request_schema = request_schema

    @property
    def resource_url(self):
        acl = self.get("ACL")
        return '%s/consumers/%s/acls' % (self.get('AdminURL'), acl.get('consumer',{}).get('id'))

provider = KongACLProvider()


def handler(request, context):
    return provider.handle(request, context)
