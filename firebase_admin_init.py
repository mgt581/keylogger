"""Firebase Admin initializer and simple auth helpers.

Usage:
 - Place your service account JSON at the project root as `serviceAccountKey.json`,
   or set the environment variable `FIREBASE_SERVICE_ACCOUNT` to its absolute path.
 - Do NOT commit the JSON file. It's ignored by `.gitignore`.

Helpers provided:
 - `init_firebase()` -> initializes and returns the app
 - `create_user(email, password, display_name=None)` -> creates a user and returns uid
 - `create_custom_token(uid)` -> returns a custom token for client sign-in
 - `verify_id_token(id_token)` -> verifies a client ID token and returns decoded claims

This file uses the Admin SDK and must run on a trusted server (not in-browser).
"""
from __future__ import annotations

import os
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials


def init_firebase() -> firebase_admin.App:
    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not cred_path:
        # default to project root serviceAccountKey.json
        base = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(base, ".."))
        default_path = os.path.join(project_root, "serviceAccountKey.json")
        if os.path.exists(default_path):
            cred_path = default_path
        else:
            # fallback to any Firebase admin JSON key in the project root
            candidate_files = [
                os.path.join(project_root, fname)
                for fname in os.listdir(project_root)
                if fname.endswith('.json') and 'firebase-adminsdk' in fname
            ]
            if len(candidate_files) == 1:
                cred_path = candidate_files[0]
            elif len(candidate_files) > 1:
                raise FileNotFoundError(
                    "Multiple Firebase admin JSON candidates found in the project root. "
                    "Set FIREBASE_SERVICE_ACCOUNT to the exact path you want to use."
                )
            else:
                cred_path = default_path

    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"Firebase service account not found at {cred_path}. "
            "Place the JSON there or set FIREBASE_SERVICE_ACCOUNT env var."
        )

    cred = credentials.Certificate(cred_path)
    return firebase_admin.initialize_app(cred)


def create_user(email: str, password: str, display_name: Optional[str] = None) -> str:
    init_firebase()
    user = auth.create_user(email=email, password=password, display_name=display_name)
    return user.uid


def create_custom_token(uid: str) -> str:
    init_firebase()
    token = auth.create_custom_token(uid)
    # firebase-admin returns bytes for custom tokens; decode to str
    return token.decode("utf-8") if isinstance(token, bytes) else token


def verify_id_token(id_token: str) -> dict:
    init_firebase()
    return auth.verify_id_token(id_token)


if __name__ == "__main__":
    print("firebase_admin_init module - helper functions available")
