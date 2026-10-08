from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from urllib.parse import urlparse
from .demo import ROOT, prepare, package
from .staging import check_staging


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, code, body, kind='application/json'):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def allowed(self):
        host = self.headers.get('Host')
        origin = self.headers.get('Origin')
        return host in self.server.hosts and (not origin or urlparse(origin).netloc == host)

    def do_GET(self):
        if not self.allowed():
            return self.reply(403, {'error': 'Unsupported origin or host'})
        assets = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css', '/favicon.svg': 'favicon.svg'}
        path = urlparse(self.path).path
        if path not in assets:
            return self.reply(404, {'error': 'Not found'})
        file = ROOT / 'web' / assets[path]
        kind = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml'}[file.suffix]
        return self.reply(200, file.read_bytes(), kind)

    def do_POST(self):
        if not self.allowed():
            return self.reply(403, {'error': 'Unsupported origin or host'})
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 2048:
                raise ValueError('Request size limit')
            data = json.loads(self.rfile.read(size))
            with self.server.lock:
                if self.path == '/api/check':
                    result = prepare(self.server.state, data['scenario'])
                    return self.reply(200, result)
                if self.path == '/api/package':
                    artifact = package(self.server.state, data['scenario'])
                    return self.reply(200, artifact.read_bytes(), 'application/zip')
                if self.path == '/api/staging':
                    from .demo import SCENARIOS
                    scenario=data['scenario']
                    if scenario not in SCENARIOS:raise ValueError('Unknown revision')
                    project=self.server.state/scenario
                    receipt=json.loads((project/'contract-receipt.json').read_text())
                    return self.reply(200,check_staging(project,receipt))
            return self.reply(404, {'error': 'Not found'})
        except (KeyError, ValueError, TypeError, OSError) as error:
            return self.reply(422, {'error': str(error)[:350]})


def make_server(port=4187, state=None):
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.hosts = {f'127.0.0.1:{server.server_port}', f'localhost:{server.server_port}'}
    server.state = Path(state) if state else ROOT / '.state' / 'demo'
    server.lock = threading.Lock()
    return server


def serve(port=4187):
    server = make_server(port)
    print(f'EvidenceGate: http://127.0.0.1:{server.server_port}', flush=True)
    server.serve_forever()
