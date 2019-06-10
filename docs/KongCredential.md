# Custom::KongCredential
The `Custom::KongCredential` creates a Kong Credential .

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
Type: Custom::KongCredential
Properties:
  AdminUrl: String
  JWT:
    Issuer: String
    PrivateKeyParameterName: String
  ServiceToken: String
  PluginName: String
  Credential:
    consumer:
      id: String
    ...
```

## Properties
You can specify the following properties:

    "AdminUrl" - pointing to the Kong Admin  (required).
    "JWT" - RS256 JWT token generator configuration (coptional).
    "JWT.Issuer" - issuer of the JWT token, defaults to 'admin'.
    "JWT.PrivateKeyParameterName" - parameter store name containing the private key to sign the token with (required).
    "ServiceToken" - pointing to the function implementing this (required)
    "PluginName" - name of the plugin for which the credentials are applicable, 'key-auth', etc. (required).
    "Credential" - object containing all the credential properties as defined by Kong plugin (required).
    "Credential.consumer_id" - id of the consumer for which the credential is relevant (required).
    "Credential..." - other properties required as the credential.


## Return values
With 'Fn::GetAtt' the following values are available:

- `id` - id of the Credential in Kong.

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
