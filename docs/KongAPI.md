# Custom::KongAPI
The `Custom::KongAPI` creates a Kong API.

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```json
{
  "Type" : "Custom::KongAPI",
  "Properties" : {
    "AdminUrl": String,
    "JWT": {
        "Issuer": String,
        "PrivateKeyParameterName": String
    },
    "ServiceToken" : String,
    "API" : {
      "name": String,
      "http_if_terminated": true,
      "https_only": false,
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

    "AdminUrl" - pointing to the Kong Admin  (required).
    "JWT" - RS256 JWT token generator configuration (optional)
    "JWT.Issuer" - issuer of the JWT token, defaults to 'admin'.
    "JWT.PrivateKeyParameterName" - parameter store name containing the private key to sign the token with (required)
    "ServiceToken" - pointing to the function implementing this resource (required)
    "API" - object containing all the properties as defined by Kong add-api (required).

Check out all properties for "API" at [add-api](https://getkong.org/docs/0.11.x/admin-api/#add-api).

## Return values
With 'Fn::GetAtt' the following values are available:

- `id` - id of the API in Kong.

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
