Firestore schema and notes
==========================

Collections:

- `users/{uid}`
  - Fields: `email` (string), `displayName` (string), `createdAt` (timestamp)
  - Access: user can read/write their own document; admins can update/delete.

- `devices/{deviceId}`
  - Fields: `owner` (uid string), `name` (string), `os` (string), `lastSeen` (timestamp), `online` (bool), `meta` (map)
  - Access: owner and admins can read/update/delete; create must set `owner` equal to authenticated uid.

- `devices/{deviceId}/logs/{logId}`
  - Fields: `timestamp`, `type`, `payload` (map or string)
  - Access: device agent (server credential with custom claim `service:true`) or owner can write; owner's and admins can read.

Design notes:
- Device agents should authenticate to your backend and receive short-lived credentials (custom tokens) for Firestore writes, or route logs through your server API which uses the Admin SDK to write to Firestore.
- Prefer server-side ingestion for logs (Admin SDK) to avoid embedding service credentials in device clients.

Security rules rationale:
- Rules allow only authenticated users to access their own records.
- Device agents should either use a service account on the server or obtain a custom token via your backend. You can add custom claims like `service: true` to mark service accounts or issued tokens used by device agents.

Deployment:

Use the Firebase CLI to deploy rules:

```bash
# install firebase-tools if needed
npm install -g firebase-tools

# login (interactive)
firebase login

# initialize in this folder, select Firestore rules
firebase init firestore

# deploy rules
firebase deploy --only firestore:rules
```

Make sure you're using Production mode and your rules deny access by default.
