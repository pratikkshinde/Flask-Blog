import sys
from pathlib import Path
from urllib.parse import parse_qs, urlencode

# Add project root directory to sys.path so app and config can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from wsgi import app


class VercelPathFixMiddleware:
    """
    WSGI Middleware to restore original request paths on Vercel Serverless.
    Vercel rewrites routes to /api/index?__vercel_path=/<path>.
    This middleware extracts the captured path, sets PATH_INFO, and cleans
    up QUERY_STRING so Flask route matching and URL generation work seamlessly.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get('QUERY_STRING', '')
        if '__vercel_path=' in qs:
            params = parse_qs(qs, keep_blank_values=True)
            vpath = params.pop('__vercel_path', ['/'])[0]
            # Normalize path
            if not vpath or vpath == '//':
                vpath = '/'
            elif vpath.startswith('//'):
                vpath = '/' + vpath.lstrip('/')
            environ['PATH_INFO'] = vpath
            environ['QUERY_STRING'] = urlencode(params, doseq=True)
        else:
            path_info = environ.get('PATH_INFO', '')
            if path_info in ('/api/index', '/api', '/api/'):
                environ['PATH_INFO'] = '/'
            elif path_info.startswith('/api/index/'):
                environ['PATH_INFO'] = path_info[10:]
            elif path_info.startswith('/api/'):
                environ['PATH_INFO'] = path_info[4:]

        environ['SCRIPT_NAME'] = ''
        return self.wsgi_app(environ, start_response)


# Wrap Flask's WSGI application with the Vercel path fix middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
