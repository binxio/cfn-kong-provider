import boto3
import sys
import uuid
import requests
import StringIO
import subprocess
from kong import handler


def test_create():
    username = 'user-%s' % uuid.uuid4()
    consumer = {'username': username}
    request = Request('Create', consumer)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    # duplicate key error
    failed_response = handler(request, {})
    assert failed_response['Status'] == 'FAILED', response['Reason']

    url = '%s/consumers/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 200, 'url %s, return %s' % (url, response.text)
    assert response.json()['username'] == username

    request = Request('Delete', consumer, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 404, 'url %s, return %s' % (url, response.text)


def test_update():
    username = 'user-%s' % uuid.uuid4()
    consumer = {'username': username}
    request = Request('Create', consumer)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    new_username = '2-%s' % username
    consumer = {'username': new_username}
    request = Request('Update', consumer, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/consumers/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 200, 'url %s, return %s' % (url, response.text)
    retrieved_consumer = response.json()
    assert retrieved_consumer['username'] == new_username

    request = Request('Delete', consumer, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']


class Request(dict):

    @property
    def admin_url(self):
        return self['ResourceProperties']['AdminURL'] if 'AdminURL' in self['ResourceProperties'] else None

    @admin_url.setter
    def admin_url(self, jwt):
        self['ResourceProperties']['AdminURL'] = jwt

    def __init__(self, request_type, consumer, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::KongConsumer',
            'LogicalResourceId': 'MyConsumer',
            'ResourceProperties': {
                'AdminURL': 'http://localhost:8001',
                'Consumer': consumer
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
