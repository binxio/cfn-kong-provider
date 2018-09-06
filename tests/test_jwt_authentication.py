import subprocess
import uuid

import boto3
import requests
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from kong import handler


def test_with_jwt():
    name = 'service-%s' % uuid.uuid4()
    admin_url, jwt_config = create_secure_admin_service(name)

    # create service without JWT
    service = {'name': 'service-%s' % uuid.uuid4(), 'host': 'localhost'}
    request = Request('Create', service)
    request.admin_url = admin_url
    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']
    assert 'Unauthorized' in response['Reason']

    # create service with JWT
    request = Request('Create', service)
    request['ResourceProperties']['JWT'] = jwt_config
    request.admin_url = admin_url
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    physical_resource_id = response['PhysicalResourceId']

    # check create
    url = 'http://localhost:8001/services/%s' % physical_resource_id
    service_response = requests.get(url)
    assert service_response.status_code == 200, url
    assert service_response.json()['name'] == service['name']

    # update the JWT token
    service['retries'] = 100
    request = Request('Update', service, physical_resource_id)
    request.admin_url = admin_url
    request['ResourceProperties']['JWT'] = jwt_config
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # check update
    url = 'http://localhost:8001/services/%s' % physical_resource_id
    service_response = requests.get(url)
    assert service_response.status_code == 200
    assert service_response.json()['retries'] == 100

    # delete the Service
    request = Request('Delete', service, physical_resource_id)
    request['ResourceProperties']['JWT'] = jwt_config
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # check delete
    url = 'http://localhost:8001/services/%s' % physical_resource_id
    service_response = requests.get(url)
    assert service_response.status_code == 404

    # check bad private key
    request = Request('Create', service)
    request['ResourceProperties']['JWT'] = {'Issuer': 'Admin', 'PrivateKeyParameterName': 'does-not-exist'}
    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']
    assert response['Reason'].startswith('could not get private key')

    # check bad AdminURL
    request = Request('Create', service)
    request['ResourceProperties']['AdminURL'] = 'http://does-not-resolve-does-it'
    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']

    remove_secure_admin_service(name, jwt_config)


def create_secure_admin_service(name):
    private_key, public_key = create_key_pair()

    ssm = boto3.client('ssm')
    private_key_parameter_name = '/private-key/%s' % name
    ssm.put_parameter(Name=private_key_parameter_name, Type='SecureString', Value=private_key)

    # create admin service
    service = {'name': name,  'protocol': 'http', 'host': 'localhost', 'port': 8001}
    service_response = requests.post('http://localhost:8001/services', json=service)
    assert service_response.status_code == 201, service_response.text
    service_id = physical_resource_id = service_response.json()['id']

    route = {'paths': ['/admin/%s' % name], 'service': { 'id': service_id}}
    route_response = requests.post('http://localhost:8001/routes', json=route)
    assert route_response.status_code == 201, route_response.text

    # add jwt plugin
    plugin = {'name': 'jwt', 'service_id': service_id}
    plugin_response = requests.post('http://localhost:8001/plugins', json=plugin)
    assert plugin_response.status_code == 201 or plugin_response.status_code == 200

    # create consumer
    url = 'http://localhost:8001/consumers'
    consumer_response = requests.post(url, json={'username': name})
    assert consumer_response.status_code == 201

    # add credential
    url = 'http://localhost:8001/consumers/%s/jwt' % name
    creds_response = requests.post(url, json={'key': name, 'rsa_public_key': public_key, 'algorithm': 'RS256'})
    assert creds_response.status_code == 201, creds_response.text
    return 'http://localhost:8000/admin/%s' % name, {'Issuer': name, 'PrivateKeyParameterName': private_key_parameter_name}


def remove_secure_admin_service(name, jwt_config):
    # cleanup service and consumer and parameter.
    url = 'http://localhost:8001/services/%s' % name

    routes = requests.get('%s/routes' % url).json()
    for route_id in map(lambda r: r['id'], routes['data']):
        route_response = requests.delete('http://localhost:8001/routes/%s' % route_id)
        assert route_response.status_code == 204, route_response.text

    service_response = requests.delete(url)
    assert service_response.status_code == 204, service_response.text

    url = 'http://localhost:8001/consumers/%s' % name
    service_response = requests.delete(url)
    assert service_response.status_code == 204

    ssm = boto3.client('ssm')
    ssm.delete_parameter(Name=jwt_config['PrivateKeyParameterName'])


def create_key_pair():
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_bytes = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption())
    private_key = private_bytes.decode('ascii')

    p = subprocess.Popen(["openssl", "rsa", "-inform", "PEM", "-pubout"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    public_key, err = p.communicate(private_key)
    return (private_key, public_key)


class Request(dict):

    @property
    def admin_url(self):
        return self['ResourceProperties']['AdminURL'] if 'AdminURL' in self['ResourceProperties'] else None

    @admin_url.setter
    def admin_url(self, jwt):
        self['ResourceProperties']['AdminURL'] = jwt

    @property
    def jwt(self):
        return self['ResourceProperties']['JWT'] if 'JWT' in self['ResourceProperties'] else None

    @jwt.setter
    def jwt(self, jwt):
        self['ResourceProperties']['JWT'] = jwt

    @property
    def service(self):
        return self['ResourceProperties']['Service'] if 'Service' in self['ResourceProperties'] else None

    @service.setter
    def service(self, service):
        self['ResourceProperties']['Service'] = service

    def __init__(self, request_type, service, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::KongService',
            'LogicalResourceId': 'MyService',
            'ResourceProperties': {
                'AdminURL': 'http://localhost:8001',
                'Service': service
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
