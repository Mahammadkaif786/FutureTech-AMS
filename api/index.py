import os
import sys

# Prepend project root directory to sys.path for Vercel serverless environment
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

class VercelPathFix:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Extract the real requested path from Vercel headers / WSGI environment
        raw_uri = (
            environ.get('HTTP_X_FORWARDED_URI') or 
            environ.get('RAW_URI') or 
            environ.get('REQUEST_URI')
        )
        
        if raw_uri:
            path = raw_uri.split('?')[0]
            if path:
                environ['PATH_INFO'] = path
        else:
            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith('/api/index'):
                new_path = path_info[10:]
                environ['PATH_INFO'] = new_path if new_path != '' else '/'
            elif '(.*)' in path_info or path_info == '/(.*)':
                matched = environ.get('HTTP_X_MATCHED_PATH', '')
                if matched and not '(.*)' in matched:
                    environ['PATH_INFO'] = matched
                else:
                    environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFix(app.wsgi_app)



