from cfn_kong_provider import KongProvider
import requests

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
                "consumer": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {
                            "type": "string"
                        }
                    }
                },
                "service": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {
                            "type": "string"
                        }
                    }
                },
                "route": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {
                            "type": "string"
                        }
                    }
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

    # override
    def transform_before_patch(self, property_name):
        new_config = self.get(property_name)
        if new_config['name'] == 'rate-limiting':
            old_config = self.get_old(property_name)
            removed_settings = {key: None for key in old_config['config'].keys() - new_config['config'].keys()}
            new_config['config'].update(removed_settings)
        return new_config


provider = KongPluginProvider()


def handler(request, context):
    return provider.handle(request, context)
