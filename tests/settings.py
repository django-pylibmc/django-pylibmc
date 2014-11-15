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
        'USERNAME': 'test_username',
        'PASSWORD': 'test_password',
        'OPTIONS': {
            'tcp_nodelay': True,
            'ketama': True
        }
    }
}

PYLIBMC_MIN_COMPRESS_LEN = 150 * 1024
PYLIBMC_COMPRESS_LEVEL = 1  # zlib.Z_BEST_SPEED

SECRET_KEY = 'secret'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
