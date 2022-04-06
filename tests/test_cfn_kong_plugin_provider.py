import uuid

import requests

from kong import handler
from test_cfn_kong_service_provider import Request as ServiceRequest


def clean_plugins():
    request = Request('Create', {})
    url = '%s/plugins' % request.admin_url
    response = requests.get(url)
    if response.status_code == 200:
        plugins = response.json()['data']
        for plugin in plugins:
            response = requests.delete('%s/plugins/%s' % (request.admin_url, plugin['id']))

    url = '%s/services' % request.admin_url
    response = requests.get(url)
    if response.status_code == 200:
        plugins = response.json()['data']
        for plugin in plugins:
            response = requests.delete('%s/services/%s' % (request.admin_url, plugin['id']))


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


def test_create_on_service():
    clean_plugins()

    service = {'name': 'service-%s' % uuid.uuid4(),  'host': 'localhost'}
    request = ServiceRequest('Create', service)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    service_id = response['PhysicalResourceId']

    plugin = {'name': 'http-log', 'service': {'id': service_id}, 'config': {'http_endpoint': 'http://log-forwarder:4443'}}
    request = Request('Create', plugin)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    url = '%s/plugins?service_id=%s&id=%s' % (request.admin_url, service_id, physical_resource_id)
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


def test_update_rate_limiting():
    plugin = {'name': 'rate-limiting', 'config': {'minute': 30}}
    first_request = Request('Create', plugin)
    response = handler(first_request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    def update(old_resource_properties, config):
        plugin = {'name': 'rate-limiting', 'config': config}
        request = Request('Update', plugin, physical_resource_id)
        request['OldResourceProperties'] = old_resource_properties
        response = handler(request, {})
        assert response['Status'] == 'SUCCESS', response['Reason']

        url = f'{request.admin_url}/plugins/{physical_resource_id}'
        response = requests.get(url)
        assert response.status_code == 200, f'url {url}, return {response.text}'
        retrieved_plugin = response.json()
        assert 'config' in retrieved_plugin
        assert 'second' in retrieved_plugin['config']
        assert 'minute' in retrieved_plugin['config']
        assert 'hour' in retrieved_plugin['config']
        for property in ['second', 'minute', 'hour']:
            assert retrieved_plugin['config'][property] == config.get(property, None)
        return request

    second_request = update(first_request['ResourceProperties'], {'hour': 60})
    third_request = update(second_request['ResourceProperties'], {'hour': 60})
    update(third_request['ResourceProperties'], {'second': 60})

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
