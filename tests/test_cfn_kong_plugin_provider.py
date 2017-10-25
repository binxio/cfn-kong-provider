import boto3
import sys
import uuid
import requests
import StringIO
import subprocess
from kong import handler


def clean_plugins():
    request = Request('Create', {})
    url = '%s/plugins?name=datadog' % request.admin_url
    response = requests.get(url)
    if response.status_code == 200:
        plugins = response.json()['data']
        for plugin in plugins:
            response = requests.delete('%s/plugins/%s' % (request.admin_url, plugin['id']))


def test_create():
    clean_plugins()

    plugin = {'name': 'datadog'}
    request = Request('Create', plugin)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    # duplicate key error
    failed_response = handler(request, {})
    assert failed_response['Status'] == 'FAILED', response['Reason']

    url = '%s/plugins/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 200, 'url %s, return %s' % (url, response.text)

    request = Request('Delete', plugin, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/plugins/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 404, 'url %s, return %s' % (url, response.text)


def test_update():
    plugin = {'name': 'datadog'}
    request = Request('Create', plugin)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    plugin = {'name': 'datadog', 'config': {'host': 'docker0'}}
    request = Request('Update', plugin, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/plugins/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 200, 'url %s, return %s' % (url, response.text)
    retrieved_plugin = response.json()
    assert 'config' in retrieved_plugin
    assert 'host' in retrieved_plugin['config']
    assert retrieved_plugin['config']['host'] == 'docker0'

    request = Request('Delete', plugin, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']


def test_bad_delete():
    request = Request('Delete', {}, "NotaUUidClearly")
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert response['Reason'] != ''


class Request(dict):

    @property
    def admin_url(self):
        return self['ResourceProperties']['AdminURL'] if 'AdminURL' in self['ResourceProperties'] else None

    @admin_url.setter
    def admin_url(self, jwt):
        self['ResourceProperties']['AdminURL'] = jwt

    def __init__(self, request_type, plugin, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::KongPlugin',
            'LogicalResourceId': 'MyPlugin',
            'ResourceProperties': {
                'AdminURL': 'http://localhost:8001',
                'Plugin': plugin
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
