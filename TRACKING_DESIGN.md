Secure tracking design (high level)
=================================

This document outlines recommended patterns for safe, privacy-first device tracking.

1) Consent & Account Model
 - Obtain explicit consent before collecting any location or activity data.
 - For children <13 (COPPA) require verifiable parental consent before any collection.
 - For employees, require a signed policy and an in-app on/off toggle for off-duty behavior.

2) Data minimization & retention
 - Store only what you need. Avoid storing raw personally-identifiable payloads if possible.
 - Use server-side auto-delete for logs older than your retention window (e.g., 7/30 days).

3) Client-side encryption (optional, for sensitive data)
 - Use a symmetric key (AES-GCM) to encrypt payloads before upload.
 - Protect the symmetric key in the device's secure enclave/keystore.
 - If server-side analysis is required, use a key-escrow model: device encrypts logs, and the symmetric key is wrapped with the server's public key and uploaded separately (server unwraps and decrypts for processing).

Example (Python AES-GCM using `cryptography`)

```py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt(payload_bytes: bytes, key: bytes) -> dict:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, payload_bytes, None)
    return { 'nonce': nonce.hex(), 'ciphertext': ct.hex() }

def decrypt(nonce_hex: str, ct_hex: str, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(bytes.fromhex(nonce_hex), bytes.fromhex(ct_hex), None)
```

4) Short-lived credentials & token flow
 - Devices should not hold long-lived service-account credentials.
 - Flow: device authenticates user -> requests device credential from backend -> backend mints a short-lived custom token or issues a signed ephemeral key with limited scope -> device uses that to write logs.

5) Server-side ingestion recommended
 - Prefer sending logs to your backend (HTTPS API) where you validate, filter, and then write to Firestore via Admin SDK. This keeps Firestore rules simpler and avoids exposing service credentials to devices.

6) Auditing & Access Control
 - Log administrative actions and changes to user/device ownership.
 - Provide UI for users to export and delete their data (GDPR right to portability and erasure).

7) App store compliance
 - For iOS, ensure you follow App Store guidelines about background location and user tracking.
 - Avoid collecting advertising identifiers unless necessary and compliant.

If you'd like, I can generate:
 - A sample backend Flask endpoint issuing short-lived device tokens
 - Client-side Python/Swift/Android samples showing encrypt+upload
 - Automated tests for the Firestore rules using the Firebase emulator suite
