import uuid
from copy import copy
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

    acl = {'consumer':{'id': str(consumer_id)}, 'group': 'binx.io'}
    request = Request('Create', acl)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    acl_id = response['PhysicalResourceId']

    url = '%s/consumers/%s/acls/%s' % (request.admin_url, consumer_id, acl_id)
    r = requests.get(url)
    assert r.status_code == 200, r.text
    assert r.json()['group'] == 'binx.io'

    acl = {'consumer': {'id': str(consumer_id)}, 'group': 'xebia'}
    request = Request('Update', acl, acl_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s/acls/%s' % (request.admin_url, consumer_id, acl_id)
    r = requests.get(url)
    assert r.status_code == 200, r.text
    assert r.json()['group'] == 'xebia'

    acl = {'consumer': {'id': str(consumer_id)}, 'group': 'xebia'}
    request = Request('Delete', acl, acl_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s/acls/%s' % (request.admin_url, consumer_id, acl_id)
    r = requests.get(url)
    assert r.status_code == 404, r.text


def test_deleted_consumer_delete():
    username = 'user-%s' % uuid.uuid4()
    consumer = {'username': username}
    create_user = Request('Create', consumer)
    create_user['ResourceType'] = 'Custom::KongConsumer'
    create_user['ResourceProperties']['Consumer'] = create_user['ResourceProperties']['ACL']
    del create_user['ResourceProperties']['ACL']
    user_created = handler(create_user, {})
    assert user_created['Status'] == 'SUCCESS', user_created['Reason']
    consumer_id = user_created['PhysicalResourceId']

    acl = {'consumer':{'id': str(consumer_id)}, 'group': 'binx.io'}
    request = Request('Create', acl)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    acl_id = response['PhysicalResourceId']


    delete_user = copy(create_user)
    delete_user['RequestType'] = 'Delete'
    delete_user['PhysicalResourceId'] = consumer_id
    user_deleted = handler(delete_user, {})
    assert user_deleted['Status'] == 'SUCCESS', response['Reason']

    delete_user['RequestType'] = 'Delete'
    delete_user['PhysicalResourceId'] = consumer_id
    user_deleted = handler(delete_user, {})
    assert user_deleted['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s/acls/%s' % (request.admin_url, consumer_id, acl_id)
    r = requests.get(url)
    assert r.status_code == 404, r.text

    acl = {'consumer': {'id': str(consumer_id)}, 'group': 'binx.io'}
    request = Request('Delete', acl, acl_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']


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
