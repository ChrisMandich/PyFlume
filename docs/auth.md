
# FlumeAuth

## Overview

`FlumeAuth` is a Python class designed to interact with Flume API Authentication. This class facilitates the authentication process with the API by handling token retrieval, refreshing, verification, and managing related credentials.

## Dependencies

- pyjwt

## Initialization

To initialize the FlumeAuth object, you'll need the following parameters:

- `username`: Username to authenticate.
- `password`: Password to authenticate.
- `client_id`: API client id.
- `client_secret`: API client secret.
- `flume_token`: (Optional) Pass a Flume token to the variable.
- `http_session`: (Optional) Requests Session() object.
- `timeout`: (Optional) Requests timeout for throttling. Default value is specified in DEFAULT_TIMEOUT.

## Methods
Token Retrieval and Management

`token`
Property that returns the current JWT token.

`refresh_token()`
Method to refresh the authorization token for the session.

`retrieve_token()`
Method to return the authorization token for the session.

## Internals
There are also some internal methods that handle loading and verifying the token, such as _load_token(token) and _request_token(payload). These are used internally by the class to manage the token lifecycle.

## Example:
```python
import pyflume
auth = pyflume.FlumeAuth(
    username='your_username',
    password='your_password',
    client_id='client_id',
    client_secret='client_secret'
)
auth.retrieve_token()
print(auth.token)  # Prints the current JWT token
```