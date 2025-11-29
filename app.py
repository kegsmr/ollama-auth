import os
import json

import requests
from flask import Flask, request, Response, jsonify


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]

app = Flask(__name__)


def api_keys():
    with open('keys.json', 'r', encoding='utf-8') as file:
        return json.load(file)


@app.route('/<path:subpath>',  methods=METHODS)
def proxy(subpath):

    url = f'{OLLAMA_HOST}/{subpath}'

    method = request.method
    headers = request.headers

    if headers.get('x-api-key') not in api_keys():
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
