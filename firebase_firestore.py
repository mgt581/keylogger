"""Helper functions for Firestore access using Admin SDK.

These helpers are for server-side use only.
"""
from __future__ import annotations

from typing import Dict, Any, Optional
import time

from firebase_admin import firestore
from firebase_admin import exceptions as firebase_exceptions

from firebase_admin_init import init_firebase


def get_db():
    # ensure firebase is initialized, then return firestore client
    init_firebase()
    return firestore.client()


def create_device(owner_uid: str, device_id: str, info: Optional[Dict[str, Any]] = None) -> None:
    db = get_db()
    doc_ref = db.collection('devices').document(device_id)
    payload = {
        'owner': owner_uid,
        'name': info.get('name') if info else device_id,
        'os': info.get('os') if info else None,
        'lastSeen': firestore.SERVER_TIMESTAMP,
        'online': True,
        'meta': info.get('meta', {}) if info else {},
    }
    doc_ref.set(payload)


def update_device_heartbeat(device_id: str) -> None:
    db = get_db()
    doc_ref = db.collection('devices').document(device_id)
    doc_ref.update({'lastSeen': firestore.SERVER_TIMESTAMP, 'online': True})


def write_device_log(device_id: str, log_type: str, payload: Dict[str, Any]) -> None:
    db = get_db()
    logs_ref = db.collection('devices').document(device_id).collection('logs')
    logs_ref.add({'timestamp': firestore.SERVER_TIMESTAMP, 'type': log_type, 'payload': payload})


def get_user_devices(user_uid: str):
    db = get_db()
    docs = db.collection('devices').where('owner', '==', user_uid).stream()
    return [d.to_dict() for d in docs]


if __name__ == '__main__':
    print('firebase_firestore helpers available')
