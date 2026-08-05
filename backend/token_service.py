from __future__ import annotations

from flask import Flask, request, jsonify, render_template
from typing import Tuple, Optional

from firebase_admin_init import init_firebase, verify_id_token
from firebase_admin import auth
from firebase_firestore import create_device

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static',
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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
