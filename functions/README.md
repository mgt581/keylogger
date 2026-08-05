Cloud Functions for Firestore maintenance

Files in this folder implement scheduled and on-demand cleanup for old device logs.

Setup & deploy

1. Install Firebase CLI and login:

```bash
npm install -g firebase-tools
firebase login
```

2. Initialize functions (if not already):

```bash
cd functions
npm install
```

3. Deploy functions:

```bash
firebase deploy --only functions
```

Environment

- Set `LOG_RETENTION_DAYS` in your Functions environment config if you want a non-default retention period  (default 30 days):

```bash
firebase functions:config:set keylogger.log_retention_days="30"
```

The scheduled function runs daily and prunes logs older than the retention cutoff.

Security

- Ensure `pruneOldLogsHttp` is protected (e.g., callable function with admin claim check) before exposing it publicly.
