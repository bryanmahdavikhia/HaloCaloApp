"""
WSGI config for halocalo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""
import os

ENVIRONMENT = os.environ.get('ENV')
if ENVIRONMENT == 'PRODUCTION':
    import newrelic.agent
    newrelic.agent.initialize("/home/gitlab/halo-calo-app/newrelic-prod.ini")
    newrelic.agent.register_application()
elif ENVIRONMENT == 'STAGE':
    import newrelic.agent
    newrelic.agent.initialize("/home/gitlab/halo-calo-app/newrelic-stage.ini")
    newrelic.agent.register_application()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'halocalo.settings')

application = get_wsgi_application()
app = application
