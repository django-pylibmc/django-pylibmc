DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testing',
        'SUPPORTS_TRANSACTIONS': False,
    },
}

INSTALLED_APPS = (
    'app',
)

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': 'localhost:11211',
        'TIMEOUT': 500,
        'BINARY': True,
        'OPTIONS': {
            'tcp_nodelay': True,
            'ketama': True
        }
    }
}

