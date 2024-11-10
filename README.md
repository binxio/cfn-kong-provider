# cfn-kong-provider
A collection of CloudFormation custom providers for managing KONG API Gateway resources


## How do I add an Kong Service?
It is quite easy: you specify a CloudFormation resource of type [Custom::KongService](docs/KongService.md) and a [Custom::KongRoute](docs/KongRoute.md):

```yaml
  HeaderService:
    Type: Custom::KongService
    Properties:
      Service:
        name: header-service
        host: httpbin.org
        protocol: https

      AdminURL: !Ref 'AdminURL'
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-kong-provider'

  HeaderRoute:
    Type: Custom::KongRoute
    Properties:
      Route:
        paths:
          - /headers
        service: 
          id: !Ref 'HeaderService'
      AdminURL: !Ref 'AdminURL'
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-kong-provider'
```

The `Service` object takes all properties as defined by [add-service](https://getkong.org/docs/0.13.x/admin-api/#add-service) except `url`.
The `Route` object takes all properties as defined by [add-route](https://getkong.org/docs/0.13.x/admin-api/#add-route).


## How do I add a Plugin?
You specify a CloudFormation resource of type [Custom::KongPlugin](docs/KongPlugin.md), as follows:

```yaml
  KeyAuthPlugin:
    Type: Custom::KongPlugin
    Properties:
      Plugin:
        name: key-auth
        service:id: !Ref 'HeaderService'
      AdminURL: !Ref 'AdminURL'
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-kong-provider'
```

the `Plugin` object takes all properties as defined by [add-plugin](https://getkong.org/docs/0.13.x/admin-api/#add-plugin).

## How do I add a Consumer?
You specify a CloudFormation resource of type [Custom::KongConsumer](docs/KongConsumer.md), as follows:

```yaml
  KongConsumer:
    Type: Custom::KongConsumer
    Properties:
      Consumer:
        username: johndoe
      AdminURL: !Ref 'AdminURL'
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-kong-provider'
```

The `Consumer` object takes all properties as defined by [add-consumer](https://getkong.org/docs/0.13.x/admin-api/#add-consumer).


You can also add credentials with [Custom::KongCredential](docs/KongCredential.md) and ACLs with [Custom::KongACL](docs/KongACL.md) to the consumer.


## Installation
To install these custom resources, type:

```sh
aws cloudformation create-stack \
	--capabilities CAPABILITY_IAM \
	--stack-name cfn-kong-provider \
	--template-body file://cloudformation/cfn-resource-provider.yaml

aws cloudformation wait stack-create-complete  --stack-name cfn-kong-provider 
```

This CloudFormation template will use our pre-packaged provider from `463637877380.dkr.ecr.eu-central-1.amazonaws.com/xebia/cfn-kong-provider:1.0.0`.


## Demo
For the demo to work, we need a deployed Kong API Gateway that is accessible from the Internet. If you do
*not* have one, type:

```sh
cd tests
./start-docker.sh
ADMIN_URL=$(curl -sS  http://localhost:4040/api/tunnels/ | jq -r '.tunnels| map(select(.proto == "http")|.)[0].public_url ')
export ADMIN_URL
```
Note that it will create an entire Kong setup, including a VPC, loadbalancers and a Postgres Database. Do not forget to clean up
afterwards.

```sh
aws cloudformation create-stack --stack-name cfn-kong-provider-demo \
	--template-body file://cloudformation/demo-stack.yaml \
	--parameters ParameterKey=AdminURL,ParameterValue=$ADMIN_URL

aws cloudformation wait stack-create-complete  --stack-name cfn-kong-provider-demo
```
To validate the result, type:
```
curl $ADMIN_URL/services/header-service
curl $ADMIN_URL/services/header-service/plugins
curl $ADMIN_URL/consumers/johndoe
curl $ADMIN_URL/consumers/johndoe/acls
curl $ADMIN_URL/consumers/johndoe/basic-auth
curl $ADMIN_URL/consumers/johndoe/key-auth
```

## Note
As of version 0.5.0 we added support for Kong `service` and `route` API objects and deprecated support for the Kong `api` API object. 
As of version 0.6.0 we have dropped support for Custom::KongAPI and Kong API version 0.x. 

# Upgrading from 0.5.x
- Custom::KongAPI resources should be replaced by a Custom::KongService and Custom::KongRoute pair.
- Anywhere reference to consumer\_id, service\_id or route\_id should be replaced with the nested construct `"<consumer|service|route>": { "id": "<id>" }` or it's yaml equivalent.
