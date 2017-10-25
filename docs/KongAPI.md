# Custom::KongAPI
The `Custom::KongAPI` creates a Kong API .

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```json
{
  "Type" : "Custom::KongAPI",
  "Properties" : {
    "Name": String
    "AdminUrl": String,
    "JWT": {
        "Issuer": String,
        "PrivateKeyParameterName": String
    },
    "ServiceToken" : String,
    "API" : {
      "http_if_terminated": false,
      "https_only": true,
      "preserve_host": false,
      "retries": 5,
      "strip_uri": true,
      "upstream_connect_timeout": 60000,
      "upstream_read_timeout": 60000,
      "upstream_send_timeout": 60000,
      "upstream_url": "http://httpbin.org"
    }
  }
}
```

## Properties
You can specify the following properties:

    "Name" - of the API.
    "AdminUrl" - pointing to the Kong Admin 
    "JWT.Issuer" - issuer of the JWT token
    "JWT.PrivateKeyParameterName" - parameter store name containing the private key to sign the token with
    "ServiceToken" - pointing to the function implementing this
    "API" - object containing all the properties as defined by [add-api](https://getkong.org/docs/0.11.x/admin-api/#add-api)


## Return values
With 'Fn::GetAtt' the following values are available:

- `id` - id of the API in Kong.

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
