from flask_appbuilder.security.manager import AUTH_OID
from superset.security import SupersetSecurityManager
from flask_oidc import OpenIDConnect
from flask_appbuilder.security.views import AuthOIDView

#from flask_login import login_user

from superset import app

from cachelib.redis import RedisCache
from celery.schedules import crontab

# PostgreSQL as the metadata database
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://superset_prod_user:superset_password@localhost/superset_prod_db'

# Redis configuration for caching
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 0,
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
}

DATA_CACHE_CONFIG = CACHE_CONFIG

# Celery configuration for async tasks
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Schedule periodic tasks
CELERY_BEAT_SCHEDULE = {
    'reports.scheduler': {
        'task': 'superset.tasks.scheduler.run_scheduled_reports',
        'schedule': crontab(minute='*/1'),
    }
}

# Secret Key for signing cookies
SECRET_KEY = "f201a0a4804c9d9b35d4d043b5acf2fefc540a07b663553cc4b8dc787cef42dd"

PREVENT_UNSAFE_DB_CONNECTIONS = False

LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    "es": {"flag": "es", "name": "Spanish"},
}


FEATURE_FLAGS = {
    'PRESTO_EXPAND_DATA': False,
    'ENABLE_TEMPLATE_PROCESSING': True
}


##################### KEYCLOAK ############################

from flask_appbuilder.security.manager import AUTH_OAUTH
from authlib.integrations.flask_client import OAuth

# Enable OAuth authentication
AUTH_TYPE = AUTH_OAUTH
#AUTH_TYPE = AUTH_OID
LOGOUT_REDIRECT_URL='http://localhost:8080/realms/superset-realm/protocol/openid-connect/logout'
#AUTH_USER_REGISTRATION = True
#AUTH_USER_REGISTRATION_ROLE = 'Alpha'
#AUTH_USER_REGISTRATION_ROLE = 'Gamma'
# OAuth provider configuration for Keycloak
OAUTH_PROVIDERS = [
    {
        'name': 'keycloak',
        'icon': 'fa-key',
        'token_key': 'access_token',  # Keycloak uses 'access_token' for the access token
        'remote_app': {
            'client_id': 'superset-client',
            'client_secret': 'PgCLBtjjprNuPPK7h6pp2xKc55FxsMHI',
            'client_kwargs': {
                'scope': 'openid profile email',
            },
            'server_metadata_url': 'http://localhost:8080/realms/superset-realm/.well-known/openid-configuration',
            'api_base_url': 'http://localhost:8080/realms/superset-realm/protocol/',
        },
    }
    ]

AUTH_ROLE_MAPPING = {
    'superset_admin': ['Admin'],
    'superset_gamma': ['Gamma']
    }


# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
#AUTH_USER_REGISTRATION_ROLE = 'Admin'
AUTH_USER_REGISTRATION_ROLE = 'Public'

# OAuth user info mappings
OAUTH_USER_INFO = [
    ('username', 'preferred_username'),
    ('email', 'email'),
    ('first_name', 'given_name'),
    ('last_name', 'family_name'),
]
