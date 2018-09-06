import uuid

import requests

from kong import handler


def test_create():
    service = {'name': 'service-%s' % uuid.uuid4(), 'host': 'localhost'}
    request = Request('Create', service)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    # duplicate key error
    failed_response = handler(request, {})
    assert failed_response['Status'] == 'FAILED', response['Reason']

    url = '%s/services/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 200, 'url %s, return %s' % (url, response.text)
    svc = response.json()
    assert service['name'] == svc['name']
    assert 'localhost' == svc['host']
    assert 'http' == svc['protocol']
    assert 80 == svc['port']
    assert 5 == svc['retries']
    assert 60000 == svc['connect_timeout']
    assert 60000 == svc['read_timeout']
    assert 60000 == svc['write_timeout']
    assert 'path' not in svc or svc['path'] is None

    request = Request('Delete', service, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/services/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 404, 'url %s, return %s' % (url, response.text)

    url = '%s/services/%s' % (request.admin_url, service['name'])
    response = requests.get(url)
    assert response.status_code == 404, 'url %s, return %s' % (url, response.text)


def test_update():
    service = {'name': 'service-%s' % uuid.uuid4(), 'host': 'localhost'}
    request = Request('Create', service)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    service2 = service.copy()
    service2['name'] = 'new-%s' % service['name']
    service2['port'] = 443
    service2['host'] = 'httpbin.org'
    service2['protocol'] = 'https'
    service2['read_timeout'] = 600
    service2['write_timeout'] = 500
    service2['connect_timeout'] = 400
    service2['retries'] = 0
    request = Request('Update', service2, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/services/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 200, 'url %s, return %s' % (url, response.text)
    svc = response.json()
    for k in service2:
        assert service2[k] == svc[k]

    request = Request('Delete', service2, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']


class Request(dict):

    @property
    def admin_url(self):
        return self['ResourceProperties']['AdminURL'] if 'AdminURL' in self['ResourceProperties'] else None

    @admin_url.setter
    def admin_url(self, jwt):
        self['ResourceProperties']['AdminURL'] = jwt

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
