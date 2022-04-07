from cfn_kong_provider import KongProvider
from copy import deepcopy

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
    def get_patch_request(self) -> dict:
        request = self.get(self.property_name)
        if request['name'] != 'rate-limiting':
            return request

        old_request = self.get_old(self.property_name,{})
        return update_rate_limit_request(old_request, request)


def update_rate_limit_request(old_request: dict, new_request: dict) -> dict:
    """
    if the rate limit is updated, clear any old rate limit configuration
    >>> update_rate_limit_request(\
             {"config": {"second": 5, "policy": "local"}}, \
             {"config": {"hour": 100, "policy": "local"}})
    {'config': {'second': None, 'hour': 100, 'policy': 'local'}}
    >>> update_rate_limit_request(\
             {"config": {"policy": "local"}}, \
             {"config": {"hour": 100, "policy": "local"}})
    {'config': {'hour': 100, 'policy': 'local'}}
    >>> update_rate_limit_request(\
             {}, \
             {"config": {"hour": 100, "policy": "local"}})
    {'config': {'hour': 100, 'policy': 'local'}}
    >>> update_rate_limit_request(\
             {"config": {"second": 5, "policy": "local"}}, \
             {"config": {"policy": "remote"}})
    {'config': {'policy': 'remote'}}
    >>> update_rate_limit_request(\
             {"config": {"second": 5, "policy": "local"}}, \
             {})
    {}
    """
    old_config = old_request.get('config',{}) if old_request else {}
    new_config = new_request.get('config',{}) if new_request else {}

    if not old_config or not new_config:
        return new_request

    rates = {"second", "minute", "hour", "day", "month", "year"}
    if not rates.intersection(new_config.keys()):
        return new_request

    config = {key: None for key in old_request['config'].keys() - new_request['config'].keys()}
    config.update(new_config)

    new_request = deepcopy(new_request)
    new_request['config'] = config
    return new_request


provider = KongPluginProvider()


def handler(request, context):
    return provider.handle(request, context)
