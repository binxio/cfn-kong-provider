import uuid

import requests

from kong import handler


def create_service(host='localhost'):
    service_name =  'service-%s' % uuid.uuid4(),
    request = {'name': service_name, 'host': host}
    response = requests.post('http://localhost:8001/services', request)
    return response.json()['id']

def test_create():
    service_id = create_service()
    route = {'service': {'id': service_id}, 'paths': ['/put']}
    request = Request('Create', route)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    url = '%s/routes/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 200, 'url %s, return %s' % (url, response.text)
    rt = response.json()
    assert cmp(rt['paths'], route['paths']) == 0

    request = Request('Delete', route, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/routes/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 404, 'url %s, return %s' % (url, response.text)


def test_update():
    service_id = create_service()
    route = {'service': { 'id': service_id}, 'paths': ['/put']}
    request = Request('Create', route)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    physical_resource_id = response['PhysicalResourceId']

    route2 = route.copy()
    route2['paths'] = ['/put', '/PUT']
    request = Request('Update', route2, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    url = '%s/routes/%s' % (request.admin_url, physical_resource_id)
    response = requests.get(url)
    assert response.status_code == 200, 'url %s, return %s' % (url, response.text)
    rt = response.json()
    assert cmp(route2['paths'], rt['paths']) == 0

    request = Request('Delete', route2, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']


class Request(dict):

    @property
    def admin_url(self):
        return self['ResourceProperties']['AdminURL'] if 'AdminURL' in self['ResourceProperties'] else None

    @admin_url.setter
    def admin_url(self, jwt):
        self['ResourceProperties']['AdminURL'] = jwt

    def __init__(self, request_type, route, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::KongRoute',
            'LogicalResourceId': 'MyRoute',
            'ResourceProperties': {
                'AdminURL': 'http://localhost:8001',
                'Route': route
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
