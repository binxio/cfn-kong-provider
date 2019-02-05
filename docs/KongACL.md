# Custom::KongACL
The `Custom::KongACL` creates a Kong ACL .

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
Type: Custom::KongACL
Properties:
  AdminUrl: String
  JWT:
    Issuer: String
    PrivateKeyParameterName: String
  ServiceToken: String
  ACL:
    consumer_id: String
    group: String
```

## Properties
You can specify the following properties:

    "AdminUrl" - pointing to the Kong Admin  (required).
    "JWT" - RS256 JWT token generator configuration (coptional).
    "JWT.Issuer" - issuer of the JWT token, defaults to 'admin'.
    "JWT.PrivateKeyParameterName" - parameter store name containing the private key to sign the token with (required).
    "ServiceToken" - pointing to the function implementing this (required)
    "ACL" - object containing the ACL information.
    "ACL.consumer_id" - to which to apply the ACL.
    "ACL.group" - the group name.


## Return values
With 'Fn::GetAtt' the following values are available:

- `id` - id of the ACL in Kong.

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
