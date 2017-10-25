# Custom::KongPlugin
The `Custom::KongPlugin` creates a Kong Plugin .

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```json
{
  "Type" : "Custom::KongPlugin",
  "Properties" : {
    "AdminUrl": String,
    "JWT": {
        "Issuer": String,
        "PrivateKeyParameterName": String
    },
    "ServiceToken" : String,
    "Plugin" : {
      "name": String,
      "api_id": String,
      "consumer_id": String,
      "config": {
         ...
      }
    }
  }
}
```

## Properties
You can specify the following properties:

    "AdminUrl" - pointing to the Kong Admin  (required).
    "JWT" - RS256 JWT token generator configuration (coptional).
    "JWT.Issuer" - issuer of the JWT token, defaults to 'admin'.
    "JWT.PrivateKeyParameterName" - parameter store name containing the private key to sign the token with (required).
    "ServiceToken" - pointing to the function implementing this (required)
    "Plugin" - object containing all the properties as defined by [add-plugin](https://getkong.org/docs/0.11.x/admin-api/#add-plugin) (required).


## Return values
With 'Fn::GetAtt' the following values are available:

- `id` - id of the Plugin in Kong.

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
