================================
pylibmc cache backend for Django
================================

.. image:: https://travis-ci.org/jbalogh/django-pylibmc.svg
    :target: https://travis-ci.org/jbalogh/django-pylibmc

This package provides a memcached cache backend for Django using
`pylibmc <http://github.com/lericson/pylibmc>`_.  You want to use pylibmc because
it's fast.

Requirements
------------

django-pylibmc requires Django 1.5+.  It was written and tested on Python 2.7.


Installation
------------


Get it from `pypi <http://pypi.python.org/pypi/django-pylibmc>`_::

    pip install django-pylibmc

or `github <http://github.com/jbalogh/django-pylibmc>`_::

    pip install -e git://github.com/jbalogh/django-pylibmc.git#egg=django-pylibmc


Usage
-----

Your cache backend should look something like this::

    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'LOCATION': 'localhost:11211',
            'TIMEOUT': 500,
            'BINARY': True,
            'OPTIONS': {  # Maps to pylibmc "behaviors"
                'tcp_nodelay': True,
                'ketama': True
            }
        }
    }


If you want to use the memcached binary protocol, set the `BINARY` key's
value to `True` as shown above.  `BINARY` is `False` by default.

If you want to control `pylibmc behaviors
<http://sendapatch.se/projects/pylibmc/behaviors.html>`_, use the
`OPTIONS`.  `OPTIONS` is an empty dict by default.

Pylibmc supports `compression
<http://sendapatch.se/projects/pylibmc/misc.html#compression>`_ and the
minimum size (in bytes) of values to compress can be set via the Django
setting `PYLIBMC_MIN_COMPRESS_LEN`.  The default is 0, which is disabled.

Pylibmc 1.3.0 and above allows to configure compression level, which can
be set via the Django setting `PYLIBMC_COMPRESS_LEVEL`. It accepts the
same values as the Python `zlib <https://docs.python.org/2/library/zlib.html>`_
module. Please note that pylibmc changed the default from `1` (`Z_BEST_SPEED`)
to `-1` (`Z_DEFAULT_COMPRESSION`) in 1.3.0.


Configuration with Environment Variables
----------------------------------------

Optionally, the memcached connection can be configured with environment
variables (on platforms like Heroku). To do so, declare the following
variables:

* `MEMCACHE_SERVERS`
* `MEMCACHE_USERNAME`
* `MEMCACHE_PASSWORD`


Caveats
-------

This package breaks away from the current handling of ``timeout=0`` in Django.
Django converts 0 into the default timeout, while django-pylibmc leaves it as
0.  memcached takes 0 to mean "infinite timeout."  You can still pass ``None``
to get the default timeout.


Testing
-------

Install `tox <http://tox.testrun.org/>`_::

    pip install tox

Run the tests like this::

    tox
