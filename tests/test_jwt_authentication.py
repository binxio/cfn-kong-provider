import boto3
import sys
import uuid
import requests
import StringIO
import subprocess
from kong import handler
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend


def test_with_jwt():
    name = 'api-%s' % uuid.uuid4()
    admin_url, jwt_config = create_secure_admin_api(name)

    # create api without JWT
    api = {'name': 'api-%s' % uuid.uuid4(),  'uris': ['/headers'], 'upstream_url': 'https://httpbin.org/headers'}
    request = Request('Create', api)
    request.admin_url = admin_url
    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']

    # create api with JWT
    request = Request('Create', api)
    request['ResourceProperties']['JWT'] = jwt_config
    request.admin_url = admin_url
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    physical_resource_id = response['PhysicalResourceId']

    # check create
    url = 'http://localhost:8001/apis/%s' % physical_resource_id
    api_response = requests.get(url)
    assert api_response.status_code == 200, url
    assert api_response.json()['name'] == api['name']

    # update the JWT token
    api['retries'] = 100
    request = Request('Update', api, physical_resource_id)
    request.admin_url = admin_url
    request['ResourceProperties']['JWT'] = jwt_config
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # check update
    url = 'http://localhost:8001/apis/%s' % physical_resource_id
    api_response = requests.get(url)
    assert api_response.status_code == 200
    assert api_response.json()['retries'] == 100

    # delete the API
    request = Request('Delete', api, physical_resource_id)
    request['ResourceProperties']['JWT'] = jwt_config
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # check delete
    url = 'http://localhost:8001/apis/%s' % physical_resource_id
    api_response = requests.get(url)
    assert api_response.status_code == 404

    # check bad private key
    request = Request('Create', api)
    request['ResourceProperties']['JWT'] = {'Issuer': 'Admin', 'PrivateKeyParameterName': 'does-not-exist'}
    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']
    assert response['Reason'].startswith('could not get private key')

    # check bad AdminURL
    request = Request('Create', api)
    request['ResourceProperties']['AdminURL'] = 'http://does-not-resolve-does-it'
    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']

    remove_secure_admin_api(name, jwt_config)


def create_secure_admin_api(name):
    private_key, public_key = create_key_pair()

    ssm = boto3.client('ssm')
    private_key_parameter_name = '/private-key/%s' % name
    ssm.put_parameter(Name=private_key_parameter_name, Type='SecureString', Value=private_key)

    # create admin api
    api = {'name': name,  'uris': ['/admin/%s' % name], 'upstream_url': 'http://localhost:8001', 'strip_uri': 'true'}
    api_response = requests.post('http://localhost:8001/apis', json=api)
    assert api_response.status_code == 201
    physical_resource_id = api_response.json()['id']

    # add jwt plugin
    url = 'http://localhost:8001/apis/%s/plugins' % physical_resource_id
    plugin_response = requests.post(url, json={'name': 'jwt'})
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


def remove_secure_admin_api(name, jwt_config):
    # cleanup api and consumer and parameter.
    url = 'http://localhost:8001/apis/%s' % name
    api_response = requests.delete(url)
    assert api_response.status_code == 204

    url = 'http://localhost:8001/consumers/%s' % name
    api_response = requests.delete(url)
    assert api_response.status_code == 204

    ssm = boto3.client('ssm')
    ssm.delete_parameter(Name=jwt_config['PrivateKeyParameterName'])


def create_key_pair():
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption())

    p = subprocess.Popen(["openssl", "rsa", "-inform", "PEM", "-pubout"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = p.communicate(private_key)
    public_key = out.decode()
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
    def api(self):
        return self['ResourceProperties']['API'] if 'API' in self['ResourceProperties'] else None

    @api.setter
    def api(self, api):
        self['ResourceProperties']['API'] = api

    def __init__(self, request_type, api, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::KongAPI',
            'LogicalResourceId': 'MyApi',
            'ResourceProperties': {
                'AdminURL': 'http://localhost:8001',
                'API': api
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
