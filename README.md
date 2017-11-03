# cfn-kong-provider
A collection of CloudFormation custom providers for managing KONG API Gateway resources

## How do I add an API?
It is quite easy: you specify a CloudFormation resource of type [Custom::KongAPI](docs/KongAPI.md):

```json
  "SampleApi": {
    "Type": "Custom::KongAPI",
    "Properties": {
      "AdminURL": "https://kong:8001",
      "API" : {
	"name": "headers",
	"uris": [ "/headers" ],
	"upstream_url": "https://httpbin.org",
	"strip_uri": false,
	"preserve_host": false,
	"retries": 5,
	"upstream_connect_timeout": 60000,
	"upstream_read_timeout": 60000,
	"upstream_send_timeout": 60000,
	"https_only": false,
	"http_if_terminated": true
      },
      "ServiceToken": { "Fn::Join": [ ":", [ "arn:aws:lambda", { "Ref": "AWS::Region" }, { "Ref": "AWS::AccountId" }, "function:binxio-cfn-kong-provider" ]]}
    }
  }
```
The `API` object takes all properties as defined by [add-api](https://getkong.org/docs/0.11.x/admin-api/#add-api).

If you need to access the api-id in your cloudformation module, you can reference attribute `id`.

```json
{ "Fn::GetAtt": [ "SampleApi", "id" ]}
```

## How do I add a Plugin?
You specify a CloudFormation resource of type [Custom::KongPlugin](docs/KongPlugin.md), as follows:

```json
  "DataDogPlugin": {
    "Type": "Custom::KongPlugin",
    "Properties": {
      "AdminURL": "https://kong:8001",
      "Plugin" : {
	"name": "key-auth",
	"api_id": { "Fn::GetAtt": [ "SampleApi", "id" ] },
      },
      "ServiceToken": { "Fn::Join": [ ":", [ "arn:aws:lambda", { "Ref": "AWS::Region" }, { "Ref": "AWS::AccountId" }, "function:binxio-cfn-kong-provider" ]]}
    }
  }
```
the `Plugin` object takes all properties as defined by [add-plugin](https://getkong.org/docs/0.11.x/admin-api/#add-plugin).

## How do I add a Consumer?
You specify a CloudFormation resource of type [Custom::KongConsumer](docs/KongConsumer.md), as follows:

```json
  "KongConsumer": {
    "Type": "Custom::KongConsumer",
    "Properties": {
      "AdminURL": "https://kong:8001",
      "Consumer" : {
	"username": "kong-admin",
      },
      "ServiceToken": { "Fn::Join": [ ":", [ "arn:aws:lambda", { "Ref": "AWS::Region" }, { "Ref": "AWS::AccountId" }, "function:binxio-cfn-kong-provider" ]]}
    }
  }
```
The `Consumer` object takes all properties as defined by [add-consumer](https://getkong.org/docs/0.11.x/admin-api/#add-consumer).

If you need to access the consumer id in your cloudformation module, you can reference attribute `id`.

```json
{ "Fn::GetAtt": [ "KongConsumer", "id" ]}
```

You can also add credentials with [Custom::KongCredential](docs/KongCredential.md) and ACLs with [Custom::KongACL](docs/KongACL.md) to the consumer.


## Installation
To install these custom resources, type:

```sh
aws cloudformation create-stack \
	--capabilities CAPABILITY_IAM \
	--stack-name cfn-kong-provider \
	--template-body file://cloudformation/cfn-resource-provider.json 

aws cloudformation wait stack-create-complete  --stack-name cfn-kong-provider 
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public/lambdas/cfn-kong-provider-latest.zip`.


## Demo
For the demo to work, we need a deployed Kong API Gateway that is accessible from the Internet. If you do
*not* have one, type:

```sh
aws cloudformation create-stack --stack-name kong-environment \
	--template-body file://cloudformation/kong.json \
	--parameters ParameterKey=KongKeyName,ParameterValue=#insert-your-key-name-here#

aws cloudformation wait stack-create-complete  --stack-name kong-environment

ADMIN_URL=$(aws --output text --query 'Stacks[*].Outputs[?OutputKey==`AdminURL`].OutputValue' \
		cloudformation describe-stacks --stack-name kong-environment)
```
Note that it will create an entire Kong setup, including a VPC, loadbalancers and a Postgres Database. Do not forget to clean up
afterwards.

```sh
aws cloudformation create-stack --stack-name cfn-kong-provider-demo \
	--template-body file://cloudformation/demo-stack.json \
	--parameters ParameterKey=AdminURL,ParameterValue=$ADMIN_URL

aws cloudformation wait stack-create-complete  --stack-name cfn-kong-provider-demo
```
To validate the result, type:
```
curl $ADMIN_URL/apis/header-api
curl $ADMIN_URL/apis/header-api/plugins
curl $ADMIN_URL/consumers/johndoe
curl $ADMIN_URL/consumers/johndoe/acls
curl $ADMIN_URL/consumers/johndoe/basic-auth
curl $ADMIN_URL/consumers/johndoe/key-auth
```
