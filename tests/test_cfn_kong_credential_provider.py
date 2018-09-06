import uuid

import requests

from kong import handler


def test_crud_credentials():
    username = 'user-%s' % uuid.uuid4()
    consumer = {'username': username}
    request = Request('Create', consumer)
    request['ResourceType'] = 'Custom::KongConsumer'
    request['ResourceProperties']['Consumer'] = request['ResourceProperties']['Credential']
    del request['ResourceProperties']['Credential']
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    consumer_id = response['PhysicalResourceId']

    cred = {'consumer_id': str(consumer_id),  'key': username}
    request = Request('Create', cred)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    cred_id = response['PhysicalResourceId']

    url = '%s/consumers/%s/key-auth' % (request.admin_url, consumer_id)
    r = requests.get(url)
    assert r.status_code == 200, r.text
    assert r.json()['data'][0]['key'] == username

    cred = {'consumer_id': str(consumer_id), 'key': 'bah-%s' % username}
    request = Request('Update', cred, cred_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s/key-auth' % (request.admin_url, consumer_id)
    r = requests.get(url)
    assert r.status_code == 200, r.text
    assert r.json()['data'][0]['key'] == 'bah-%s' % username

    cred = {'consumer_id': str(consumer_id)}
    request = Request('Delete', cred, cred_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s/key-auth' % (request.admin_url, consumer_id)
    r = requests.get(url)
    assert r.status_code == 200, r.text
    assert r.json()['total'] == 0, r.text


class Request(dict):

    @property
    def admin_url(self):
        return self['ResourceProperties']['AdminURL'] if 'AdminURL' in self['ResourceProperties'] else None

    @admin_url.setter
    def admin_url(self, jwt):
        self['ResourceProperties']['AdminURL'] = jwt

    def __init__(self, request_type, cred, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::KongCredential',
            'LogicalResourceId': 'MyCredential',
            'ResourceProperties': {
                'AdminURL': 'http://localhost:8001',
                'PluginName': 'key-auth',
                'Credential': cred
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
