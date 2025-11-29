import os
import json
import secrets

import requests
from flask import Flask, request, Response, jsonify


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
KEYS_JSON = 'keys.json'

app = Flask(__name__)

if not os.path.exists(KEYS_JSON):
    with open(KEYS_JSON, 'w', encoding='utf-8') as file:
        json.dump(
            {
                secrets.token_hex(32): {
                    'allowed': ['*'],
                    'denied': []
                }
            },
            file,
            indent=4
        )


def api_keys() -> dict:
    with open(KEYS_JSON, 'r', encoding='utf-8') as file:
        return dict(json.load(file))


def is_authorized(key: str, route: str):

    if not route.startswith('/'):
        route = '/' + route

    rules = api_keys().get(key)

    if not rules:
        return False

    allowed = rules.get('allowed', [])
    denied = rules.get('denied', [])

    if not isinstance(allowed, list):
        allowed = [allowed]
    if not isinstance(denied, list):
        denied = [denied]

    if route in denied:
        return False
    for d in denied:
        if route.startswith(d + '/'):
            return False

    if '*' in allowed:
        return True
    if route in allowed:
        return True
    for a in allowed:
        if route.startswith(a + '/'):
            return True

    return False


@app.route('/<path:subpath>',  methods=METHODS)
def proxy(subpath):

    url = f'{OLLAMA_HOST}/{subpath}'

    method = request.method
    headers = request.headers

    if key := headers.get('x-api-key'):
        if not is_authorized(key, subpath):
            return jsonify({'error':'Unauthorized'}), 403
    else:
        return jsonify({'error':'Unauthorized'}), 401

    headers = {k: v for k, v in headers.items()
            if k.lower() not in ['host', 'x-api-key']}

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        data=request.get_data(),
        params=request.args,
        stream=True
    )

    return Response(response.iter_content(chunk_size=1024),
                    status=response.status_code,
                    content_type=response.headers.get("content-type"))


if __name__ == "__main__":
    app.run(debug=True)
