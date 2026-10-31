import sys
from pathlib import Path

# Add project root directory to sys.path so app and config can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from wsgi import app


class VercelPathFixMiddleware:
    """
    WSGI Middleware to fix PATH_INFO on Vercel Serverless.
    When Vercel rewrites incoming traffic to /api/index, PATH_INFO
    is often set to '/api/index' instead of the user's actual URL.
    This middleware restores the original URL from Vercel's proxy headers
    so Flask routes ('/', '/explore', etc.) match accurately.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. Check Vercel proxy headers for the true browser path
        real_path = None
        for header in (
            'HTTP_X_MATCHED_PATH',
            'HTTP_X_FORWARDED_URI',
            'HTTP_X_ORIGINAL_URI',
        ):
            val = environ.get(header)
            if val and not val.startswith('/api/index'):
                real_path = val.split('?')[0]
                break

        if real_path:
            environ['PATH_INFO'] = real_path
        else:
            # 2. Fallback prefix stripping
            path_info = environ.get('PATH_INFO', '')
            if path_info in ('/api/index', '/api', '/api/'):
                environ['PATH_INFO'] = '/'
            elif path_info.startswith('/api/index/'):
                environ['PATH_INFO'] = path_info[10:]
            elif path_info.startswith('/api/'):
                environ['PATH_INFO'] = path_info[4:]

        environ['SCRIPT_NAME'] = ''
        return self.wsgi_app(environ, start_response)


# Wrap Flask's WSGI app with the path fix middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
