import uuid

import requests

from kong import handler


def test_crud():
    username = 'user-%s' % uuid.uuid4()
    consumer = {'username': username}
    request = Request('Create', consumer)
    request['ResourceType'] = 'Custom::KongConsumer'
    request['ResourceProperties']['Consumer'] = request['ResourceProperties']['ACL']
    del request['ResourceProperties']['ACL']
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    consumer_id = response['PhysicalResourceId']

    acl = {'consumer_id': str(consumer_id), 'group': 'binx.io'}
    request = Request('Create', acl)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    acl_id = response['PhysicalResourceId']

    url = '%s/consumers/%s/acls/%s' % (request.admin_url, consumer_id, acl_id)
    r = requests.get(url)
    assert r.status_code == 200, r.text
    assert r.json()['group'] == 'binx.io'

    acl = {'consumer_id': str(consumer_id), 'group': 'xebia'}
    request = Request('Update', acl, acl_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s/acls/%s' % (request.admin_url, consumer_id, acl_id)
    r = requests.get(url)
    assert r.status_code == 200, r.text
    assert r.json()['group'] == 'xebia'

    acl = {'consumer_id': str(consumer_id), 'group': 'xebia'}
    request = Request('Delete', acl, acl_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s/acls/%s' % (request.admin_url, consumer_id, acl_id)
    r = requests.get(url)
    assert r.status_code == 404, r.text


class Request(dict):

    @property
    def admin_url(self):
        return self['ResourceProperties']['AdminURL'] if 'AdminURL' in self['ResourceProperties'] else None

    @admin_url.setter
    def admin_url(self, jwt):
        self['ResourceProperties']['AdminURL'] = jwt

    def __init__(self, request_type, acl, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::KongACL',
            'LogicalResourceId': 'MyConsumer',
            'ResourceProperties': {
                'AdminURL': 'http://localhost:8001',
                'ACL': acl
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
