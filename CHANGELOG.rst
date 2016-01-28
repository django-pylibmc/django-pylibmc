Changelog
=========

Unreleased
----------
- **Backwards incompatible:** No longer override the native Django memcache
  timeout behaviour. This means that using a timeout of ``0`` now results in
  'immediately expire' rather than an infinite timeout. To maintain previous
  behaviour use ``None`` instead, consistent with the `Django documentation
  <https://docs.djangoproject.com/en/stable/topics/cache/#cache-arguments>`_.

0.6.1 - 2015-12-28
------------------
- Supports Django 1.7 through 1.9
- Supports Python 2.7, 3.4, and 3.5

0.6.0 - 2015-04-01
------------------
- Requires pylibmc 1.4.1 or greater
- Supports Django 1.4 through 1.8.
- Supports Python 2.5 through 2.7, and Python 3.3 through 3.4
- In Django 1.6 and higher, when the timeout is omitted, the default
  timeout is used, rather than set to "never expire".
