from __future__ import annotations

import os
import sys

# Ensure repo root is on sys.path when running this module directly from backend/token_service.py.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from datetime import datetime
from typing import List, Optional, Tuple

from flask import Flask, jsonify, render_template, request
from firebase_admin import auth

from firebase_admin_init import init_firebase, verify_id_token
from firebase_firestore import (
    create_device,
    get_device,
    get_devices,
    query_device_events,
    rename_device,
)

app = Flask(
    __name__,
    template_folder=os.path.join(ROOT_DIR, 'templates'),
    static_folder=os.path.join(ROOT_DIR, 'static'),
)
init_firebase()


def _require_admin() -> Tuple[Optional[dict], Optional[Tuple[str, int]]]:
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, ('Missing Authorization header', 401)
    id_token = auth_header.split(' ', 1)[1]
    try:
        claims = verify_id_token(id_token)
    except Exception as e:
        return None, (f'Invalid token: {e}', 401)
    if not claims.get('admin'):
        return None, ('Admin privileges required', 403)
    return claims, None


@app.route('/mint_device_token', methods=['POST'])
def mint_device_token():
    claims, err = _require_admin()
    if err:
        msg, code = err
        return jsonify({'error': msg}), code

    data = request.get_json() or {}
    device_id = data.get('device_id')
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400

    # Use a predictable UID for device sign-in; the client will sign in with this custom token.
    uid = f'device:{device_id}'

    # Create a custom token containing a short claim indicating this is a device/service token.
    token = auth.create_custom_token(uid, {'service': True, 'device_id': device_id})
    token_str = token.decode('utf-8') if isinstance(token, bytes) else token
    return jsonify({'custom_token': token_str})


@app.route('/admin', methods=['GET'])
def admin_page():
    return render_template('admin.html')


@app.route('/onboard', methods=['GET'])
def onboarding_page():
    return render_template('onboard.html')


@app.route('/register_phone', methods=['POST'])
def register_phone():
    data = request.get_json() or {}
    device_id = data.get('device_id')
    owner_uid = data.get('owner_uid')
    custom_token = data.get('custom_token')

    if not device_id or not owner_uid or not custom_token:
        return jsonify({'error': 'device_id, owner_uid, and custom_token are required'}), 400

    return jsonify({'status': 'ready', 'message': 'Use the app client to sign in with the custom token and register the device.'})


@app.route('/register_device', methods=['POST'])
def register_device():
    """Admin-only helper to create a device record in Firestore for testing.

    Payload: {"device_id": "...", "owner_uid": "...", "info": {...}}
    This exists to let an admin quickly register a device while testing the
    client onboarding flow (minting tokens + device registration).
    """
    claims, err = _require_admin()
    if err:
        msg, code = err
        return jsonify({'error': msg}), code

    data = request.get_json() or {}
    device_id = data.get('device_id')
    owner_uid = data.get('owner_uid')
    info = data.get('info', {})
    if not device_id or not owner_uid:
        return jsonify({'error': 'device_id and owner_uid are required'}), 400

    try:
        create_device(owner_uid, device_id, info)
    except Exception as e:
        return jsonify({'error': f'Failed to create device: {e}'}), 500

    return jsonify({'status': 'ok', 'device_id': device_id})


@app.route('/devices', methods=['GET'])
def list_devices():
    claims, err = _require_admin()
    if err:
        msg, code = err
        return jsonify({'error': msg}), code

    try:
        devices = get_devices()
        return jsonify({'devices': devices})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch devices: {e}'}), 500


@app.route('/devices/<device_id>', methods=['GET'])
def get_device_detail(device_id: str):
    claims, err = _require_admin()
    if err:
        msg, code = err
        return jsonify({'error': msg}), code

    try:
        device = get_device(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        return jsonify({'device': device})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch device: {e}'}), 500


@app.route('/devices/<device_id>/rename', methods=['POST'])
def rename_device_route(device_id: str):
    claims, err = _require_admin()
    if err:
        msg, code = err
        return jsonify({'error': msg}), code

    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    try:
        rename_device(device_id, name)
        return jsonify({'status': 'ok', 'device_id': device_id})
    except Exception as e:
        return jsonify({'error': f'Failed to rename device: {e}'}), 500


@app.route('/devices/<device_id>/events', methods=['GET'])
def query_events(device_id: str):
    claims, err = _require_admin()
    if err:
        msg, code = err
        return jsonify({'error': msg}), code

    start_ts = request.args.get('start')
    end_ts = request.args.get('end')
    categories = request.args.getlist('category')

    try:
        if not start_ts or not end_ts:
            return jsonify({'error': 'start and end query parameters are required'}), 400
        start = datetime.fromisoformat(start_ts)
        end = datetime.fromisoformat(end_ts)
        events = query_device_events(device_id, start, end, categories)
        return jsonify({'events': events})
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format; use ISO 8601'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to query events: {e}'}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
