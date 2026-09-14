# AUTHENTICATION
The extension fetches `cyberos_token` from local storage.
If the token exists, it is sent in the `Authorization: Bearer` header.
If the token is invalid, the backend enforces tenant-level access limits based on RBAC rules.
