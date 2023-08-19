"""Support constants for test_*."""
from datetime import timedelta
from types import MappingProxyType

CONST_TOKEN_FILE = "token.json"  # noqa: S105
CONST_HTTP_METHOD_POST = "post"
CONST_USERNAME = "username"  # noqa: S105
CONST_PASSWORD = "password"  # noqa: S105
CONST_CLIENT_ID = "client_id"  # noqa: S105
CONST_CLIENT_SECRET = "client_secret"  # noqa: S105
CONST_USER_ID = "user_id"
CONST_FLUME_TOKEN = MappingProxyType(
    {
        "token_type": "bearer",
        "expires_in": 604800,
        "refresh_token": "fdb8fdbecf1d03ce5e6125c067733c0d51de209c",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl9pZCIsImV4cCI6Mjk5OTk5OTk5OTcsIngiOiJ5eiJ9.utb2yzcMImBFhDx_mssC_HU0mbfo0D_-VAQOetw5_h0",
    },
)
CONST_SCAN_INTERVAL = timedelta(minutes=1)  # Using datetime
