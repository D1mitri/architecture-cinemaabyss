import os
import random
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import requests
import socket

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('ProxyServer')

PORT = int(os.getenv('PORT', 8000))
MONOLITH_URL = os.getenv('MONOLITH_URL', 'http://monolith:8080')
MOVIES_SERVICE_URL = os.getenv('MOVIES_SERVICE_URL', 'http://movies-service:8081')
EVENTS_SERVICE_URL = os.getenv('EVENTS_SERVICE_URL', 'http://events-service:8082')
GRADUAL_MIGRATION = os.getenv('GRADUAL_MIGRATION', 'true').lower() == 'true'
MIGRATION_PERCENT = int(os.getenv('MOVIES_MIGRATION_PERCENT', 50))

class ProxyHandler(BaseHTTPRequestHandler):
    def _get_target_url(self, path):
        """Определяем целевой URL на основе пути."""
        if path.startswith('/api/movies'):
            if GRADUAL_MIGRATION:
                random_value = random.randint(1, 100)
                logger.info(f"Migration check - Path: {path}, Migration Percent: {MIGRATION_PERCENT}, Random: {random_value}")

                if random_value <= MIGRATION_PERCENT:
                    logger.info(f"Routing to MOVIES_SERVICE_URL: {MOVIES_SERVICE_URL}")
                    return MOVIES_SERVICE_URL
                else:
                    logger.info(f"Routing to MONOLITH_URL: {MONOLITH_URL}")
                    return MONOLITH_URL
            else:
                logger.info(f"Gradual migration disabled, routing to MOVIES_SERVICE_URL: {MOVIES_SERVICE_URL}")
                return MOVIES_SERVICE_URL
        elif path.startswith('/events'):
            logger.info(f"Routing events to EVENTS_SERVICE_URL: {EVENTS_SERVICE_URL}")
            return EVENTS_SERVICE_URL
        elif path.startswith('/api/users'):
            logger.info(f"Routing users to MONOLITH_URL: {MONOLITH_URL}")
            return MONOLITH_URL

        logger.info(f"Default routing to MONOLITH_URL: {MONOLITH_URL}")
        return MONOLITH_URL

    def _forward_request(self, method):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        target_url = self._get_target_url(path)
        full_url = f"{target_url}{self.path}"

        logger.info(f"Received {method} {self.path}")
        logger.info(f"Forwarding to: {full_url}")

        headers = {k: v for k, v in self.headers.items()}
        headers.pop('Host', None)

        try:
            target_host = urlparse(target_url).hostname
            target_port = urlparse(target_url).port or 80
            with socket.create_connection((target_host, target_port), timeout=5):
                pass
        except (socket.gaierror, socket.timeout, ConnectionRefusedError) as e:
            logger.error(f"Service {target_url} is unreachable: {str(e)}")
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"502 Bad Gateway: Service {target_host}:{target_port} is down".encode())
            return

        try:
            resp = requests.request(
                method,
                full_url,
                headers=headers,
                data=self.rfile.read(int(self.headers.get('Content-Length', 0))) if method in ['POST', 'PUT', 'PATCH'] else None,
                timeout=10
            )

            logger.info(f"Response from {target_url}: {resp.status_code}")
            logger.debug(f"Response headers: {dict(resp.headers)}")

            self.send_response(resp.status_code)
            for header, value in resp.headers.items():
                if header.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(header, value)
            self.end_headers()
            self.wfile.write(resp.content)

        except requests.exceptions.RequestException as e:
            logger.error(f"Proxy error: {str(e)}")
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"502 Bad Gateway: {str(e)}".encode())

    def do_GET(self):
        self._forward_request('GET')

    def do_POST(self):
        self._forward_request('POST')

    def do_PUT(self):
        self._forward_request('PUT')

    def do_DELETE(self):
        self._forward_request('DELETE')

if __name__ == '__main__':
    logger.info(f"Starting proxy server on port {PORT}")
    logger.info(f"Monolith URL: {MONOLITH_URL}")
    logger.info(f"Movies Service URL: {MOVIES_SERVICE_URL}")
    logger.info(f"Events Service URL: {EVENTS_SERVICE_URL}")
    logger.info(f"Gradual Migration: {GRADUAL_MIGRATION}")
    logger.info(f"Migration Percent: {MIGRATION_PERCENT}%")

    server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    server.serve_forever()