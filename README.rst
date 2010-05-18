================================
pylibmc cache backend for Django
================================

This package provides a memcached cache backend for Django using
`pylibmc <http://github.com/lericson/pylibmc>`_.  You want to use pylibmc because
it's fast.


Requirements
------------

django-pylibmc requires Django 1.2.  It was written and tested on Python 2.6.


Installation
------------


Get it from `pypi <http://pypi.python.org/pypi/django-pylibmc>`_::

    pip install django-pylibmc

or `github <http://github.com/jbalogh/django-pylibmc>`_::

    pip install -e git://github.com/jbalogh/django-pylibmc.git#egg=django-pylibmc


Usage
-----

Your cache backend should look something like this::

    CACHE_BACKEND = 'django_pylibmc.memcached://localhost:11211?timeout=500'

If you want to use the memcached binary protocol, pass ``binary=1`` in your
``CACHE_BACKEND``::

    CACHE_BACKEND = 'django_pylibmc.memcached://localhost:11211?timeout=500&binary=1'

If you want to control `pylibmc behaviors
<http://sendapatch.se/projects/pylibmc/behaviors.html>`_, use the setting
called ``PYLIBMC_BEHAVIORS``::

    PYLIBMC_BEHAVIORS = {'tcp_nodelay': True, 'ketama': True}

``PYLIBMC_BEHAVIORS`` is an empty dict by default.


Caveats
-------

This package breaks away from the current handling of ``timeout=0`` in Django.
Django converts 0 into the default timeout, while django-pylibmc leaves it as
0.  memcached takes 0 to mean "infinite timeout."  You can still pass ``None``
to get the default timeout.
