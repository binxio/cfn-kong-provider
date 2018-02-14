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

    def create(self):
        if 'api_id' in self.get('Plugin'):
            self.create_on_api()
        else:
            super(KongPluginProvider, self).create()

    def create_on_api(self):
        """
        we noticed that creating a plugin on an API through the /plugins interface
        did not activate the http-log plugin. So, we create it on the /apis/<api>/plugins
        interface instead.
        """
        if self.add_jwt():
            try:
                url = '%s/apis/%s/plugins' % (self.get('AdminURL'), self.get('Plugin').get('api_id'))
                properties = self.get('Plugin').copy()
                del properties['api_id']
                response = requests.post(url, headers=self.headers, json=properties)
                if response.status_code in (200, 201):
                    r = response.json()
                    self.physical_resource_id = r['id']
                    self.set_attribute('id', self.physical_resource_id)
                else:
                    self.physical_resource_id = 'failed-to-create'
                    self.fail('Could not create the %s, %s' % (self.property_name, response.text))
            except IOError as e:
                self.physical_resource_id = 'failed-to-create'
                self.fail('Could not create the %s, %s' % (self.property_name, str(e)))
        else:
            self.physical_resource_id = 'failed-to-create'

provider = KongPluginProvider()


def handler(request, context):
    return provider.handle(request, context)
