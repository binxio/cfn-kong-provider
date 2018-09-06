# Custom::KongRoute
The `Custom::KongRoute` creates a Kong Route

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```json
{
  "Type" : "Custom::KongRoute",
  "Properties" : {
    "AdminUrl": String,
    "JWT": {
        "Issuer": String,
        "PrivateKeyParameterName": String
    },
    "RouteToken" : String,
    "Route" : {
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
    "RouteToken" - pointing to the function implementing this resource (required)
    "Route" - object containing all the properties as defined by Kong add-route, except `url` (required).

Check out all properties for "Route" at [add-route](https://getkong.org/docs/0.13.x/admin-api/#add-route).

## Return values
With 'Fn::GetAtt' the following values are available:

- `id` - id of the Route in Kong.

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
