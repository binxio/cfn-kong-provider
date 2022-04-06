import boto3
import requests
from botocore.exceptions import ClientError
from cfn_resource_provider import ResourceProvider
from jwt_generator import JWTGenerator


class KongProvider(ResourceProvider):

    def __init__(self, resource_name, property_name):
        assert resource_name is not None
        assert property_name is not None
        super(KongProvider, self).__init__()
        self.headers = {}
        self.ssm = boto3.client('ssm')
        self.resource_name = resource_name  # eg. plugins, consumers, apis
        self.property_name = property_name  # eg. Plugin, Consumer, API

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def add_jwt(self):
        if 'Authorization' in self.headers:
            del self.headers['Authorization']

        if self.get('JWT') is not None:
            config = self.get('JWT')
            try:
                response = self.ssm.get_parameter(Name=config['PrivateKeyParameterName'], WithDecryption=True)
                private_key = response['Parameter']['Value']

                jwt = JWTGenerator()
                jwt.issuer = config['Issuer']
                jwt.set_private_key(private_key.encode('ascii'))
                jwt.generate()

                self.headers['Authorization'] = 'Bearer %s' % jwt.token
            except ClientError as e:
                self.fail('could not get private key, %s' % e.response['Error'])
                return False
        return True

    @property
    def resource_url(self):
        return '%s/%s' % (self.get('AdminURL'), self.resource_name)

    def create(self):
        if self.add_jwt():
            try:
                response = requests.post(self.resource_url, headers=self.headers, json=self.get(self.property_name))
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

    def update(self):
        if self.add_jwt():
            url = '%s/%s' % (self.resource_url, self.physical_resource_id)

            try:
                json = self.transform_before_patch(self.property_name)
                response = requests.patch(url, headers=self.headers, json=json)
                if response.status_code in (200, 201):
                    r = response.json()
                    self.physical_resource_id = r['id']
                    self.set_attribute('id', self.physical_resource_id)
                else:
                    self.fail('Could not update the %s, %s' % (self.property_name, response.text))
            except IOError as e:
                self.fail('Could not update the %s, %s' % (self.property_name, str(e)))

    def transform_before_patch(self, property_name):
        return self.get(property_name)

    def delete(self):
        if self.add_jwt():
            url = '%s/%s' % (self.resource_url, self.physical_resource_id)

            try:
                response = requests.delete(url, headers=self.headers)
                if response.status_code in (200, 204, 404):
                    pass
                elif response.status_code == 400:
                    self.success('delete failed, %s' % response.text)
                else:
                    self.fail('Could not delete the %s, %s' % (self.property_name, response.text))
            except IOError as e:
                self.fail('Could not delete the %s, %s' % (self.property_name, str(e)))
