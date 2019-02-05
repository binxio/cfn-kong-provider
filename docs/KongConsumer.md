# Custom::KongConsumer
The `Custom::KongConsumer` creates a Kong Consumer.

Support for credentials is not yet available, making this resource slightly less useful at this time.

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
Type: Custom::KongConsumer
Properties:
  AdminUrl: String
  JWT:
    Issuer: String
    PrivateKeyParameterName: String
  ServiceToken: String
  Consumer:
    username: String
    custom_id: String
```

## Properties
You can specify the following properties:

    "AdminUrl" - pointing to the Kong Admin (required).
    "JWT" - RS256 JWT token generator configuration (optional).
    "JWT.Issuer" - issuer of the JWT token, defaults to 'admin'.
    "JWT.PrivateKeyParameterName" - parameter store name containing the private key to sign the token with (required).
    "ServiceToken" - pointing to the function implementing this resource (required).
    "Consumer" - object containing all the properties as defined by add-consumer (required).

Check out all properties for "Plugin" at [add-consumer](https://getkong.org/docs/0.11.x/admin-api/#add-consumer).
 
## Return values
With 'Fn::GetAtt' the following values are available:

- `id` - id of the Consumer in Kong.

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
