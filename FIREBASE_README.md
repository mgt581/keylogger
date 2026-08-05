Firebase Admin setup (server-side)
=================================

1) Place your service account JSON file in the project root and name it `serviceAccountKey.json`, or set the absolute path in the environment variable `FIREBASE_SERVICE_ACCOUNT`.

2) Install dependencies in the project's venv:

```bash
cd /Users/alexb/Desktop/keylogger
./.venv/bin/python -m pip install -r requirements.txt
```

3) Example usage:

```python
from firebase_admin_init import create_user, create_custom_token, verify_id_token

# create a user (server side)
uid = create_user('alice@example.com', 'securePassword123', display_name='Alice')

# create a custom token for client sign-in
token = create_custom_token(uid)

# verify an ID token received from client
claims = verify_id_token('<id_token_from_client>')
```

Security notes:
- Keep the service account JSON out of version control. `.gitignore` already ignores common patterns.
- The Admin SDK must only run on a trusted server.
