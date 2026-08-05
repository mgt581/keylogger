from __future__ import annotations

from flask import Flask, request, jsonify
from typing import Tuple, Optional

from firebase_admin_init import init_firebase, verify_id_token
from firebase_admin import auth

app = Flask(__name__)
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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
