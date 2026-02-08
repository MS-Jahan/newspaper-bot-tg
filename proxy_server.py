import os
from flask import Flask, request, Response
from curl_cffi import requests

import logging
from logging.handlers import RotatingFileHandler
from waitress import serve

# Configure logging
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
log_file = 'proxy_server.log'
# 1 MB max size, 10 backup files
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

app = Flask(__name__)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Load API key from env
# Load API key from env
PROXY_API_KEY = os.environ.get('PROXY_API_KEY')
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB limit

@app.route('/fetch', methods=['POST'])
def fetch():
    # Check API key if configured
    if PROXY_API_KEY:
        auth_header = request.headers.get('X-API-KEY')
        if not auth_header or auth_header != PROXY_API_KEY:
            return {"error": "Unauthorized"}, 401

    data = request.json
    if not data or 'url' not in data:
        return {"error": "URL is required"}, 400

    url = data.get('url')
    headers = data.get('headers', {})
    impersonate = data.get('impersonate', 'chrome')
    timeout = data.get('timeout', 60)
    
    # Handle verify/proxies if needed, but for now user just wants to run on local
    verify = data.get('verify', False)

    try:
        app.logger.info(f"Fetching: {url}")
        # Enable streaming to handle files (PDFs, Images) efficiently
        resp = requests.get(
            url,
            headers=headers,
            impersonate=impersonate,
            timeout=timeout,
            verify=verify,
            stream=True
        )
        app.logger.info(f"Successfully connected to {url} - Status: {resp.status_code}")
        
        # Check content length if available
        content_length = resp.headers.get('content-length')
        if content_length and int(content_length) > MAX_FILE_SIZE:
            app.logger.warning(f"File too large: {content_length} bytes. Limit is {MAX_FILE_SIZE} bytes.")
            resp.close()
            return {"error": "File too large"}, 413

        # Create response with correct content type and headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.headers.items()
                   if name.lower() not in excluded_headers]

        def generate():
            try:
                for chunk in resp.iter_content(chunk_size=4096):
                    if chunk:
                        yield chunk
                app.logger.info(f"Finished streaming {url}")
            except Exception as e:
                app.logger.error(f"Error during streaming {url}: {e}")

        return Response(generate(), status=resp.status_code, headers=headers)

    except Exception as e:
        app.logger.error(f"Error fetching {url}: {e}")
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Production server using waitress
    app.logger.info(f"Starting proxy server on port {port}")
    serve(app, host='0.0.0.0', port=port)
