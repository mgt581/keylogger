"""Helper functions for Firestore access using Admin SDK.

These helpers are for server-side use only.
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List, Iterable
from datetime import datetime

from firebase_admin import firestore

from firebase_admin_init import init_firebase


def get_db():
    init_firebase()
    return firestore.client()


def create_device(owner_uid: str, device_id: str, info: Optional[Dict[str, Any]] = None) -> None:
    db = get_db()
    doc_ref = db.collection('devices').document(device_id)
    payload = {
        'owner': owner_uid,
        'name': info.get('name') if info else device_id,
        'participantName': info.get('participantName') if info else None,
        'model': info.get('model') if info else None,
        'os': info.get('os') if info else None,
        'online': info.get('online', True) if info else True,
        'lastSeen': firestore.SERVER_TIMESTAMP,
        'lastSync': firestore.SERVER_TIMESTAMP,
        'battery': info.get('battery'),
        'sessionActive': info.get('sessionActive', False) if info else False,
        'meta': info.get('meta', {}) if info else {},
    }
    doc_ref.set(payload, merge=True)


def rename_device(device_id: str, name: str) -> None:
    db = get_db()
    doc_ref = db.collection('devices').document(device_id)
    doc_ref.update({'name': name})


def get_devices() -> List[Dict[str, Any]]:
    db = get_db()
    docs = db.collection('devices').stream()
    return [dict({'deviceId': doc.id}, **doc.to_dict()) for doc in docs]


def get_device(device_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    doc = db.collection('devices').document(device_id).get()
    return dict({'deviceId': doc.id}, **doc.to_dict()) if doc.exists else None


def query_device_events(
    device_id: str,
    start_time: datetime,
    end_time: datetime,
    categories: Optional[Iterable[str]] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    db = get_db()
    events_ref = db.collection('devices').document(device_id).collection('events')
    query = events_ref.where('timestamp', '>=', start_time).where('timestamp', '<=', end_time)

    if categories:
        types = list(categories)
        if len(types) == 1:
            query = query.where('eventType', '==', types[0])
        else:
            query = query.where('eventType', 'in', types)

    query = query.order_by('timestamp').limit(limit)
    docs = query.stream()
    events = []
    for doc in docs:
        data = doc.to_dict()
        if 'timestamp' in data and hasattr(data['timestamp'], 'isoformat'):
            data['timestamp'] = data['timestamp'].isoformat()
        data['eventId'] = doc.id
        events.append(data)
    return events


def create_device_event(device_id: str, event_type: str, payload: Dict[str, Any], extra: Optional[Dict[str, Any]] = None) -> None:
    db = get_db()
    events_ref = db.collection('devices').document(device_id).collection('events')
    event_data = {
        'deviceId': device_id,
        'eventType': event_type,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'payload': payload,
    }
    if extra:
        event_data.update(extra)
    events_ref.add(event_data)


if __name__ == '__main__':
    print('firebase_firestore helpers available')
