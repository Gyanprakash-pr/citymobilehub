import os
import sys

# The path to your GitHub repository folder on PythonAnywhere
path = '/home/citymobilehub/citymobilehub'
if path not in sys.path:
    sys.path.append(path)

# Pointing to your Django project's settings file
os.environ['DJANGO_SETTINGS_MODULE'] = 'OnlineBazar.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()