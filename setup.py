"""django-pylibmc packaging."""
from __future__ import unicode_literals
from codecs import open
import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import django_pylibmc


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


def get_long_description(title):
    """Create the long_description from other files."""
    ROOT = os.path.abspath(os.path.dirname(__file__))

    readme = open(os.path.join(ROOT, 'README.rst'), 'r', 'utf8').read()
    body_tag = ".. Omit badges from docs"
    readme_body_start = readme.index(body_tag)
    assert readme_body_start
    readme_body = readme[readme_body_start + len(body_tag):]

    changelog = open(os.path.join(ROOT, 'CHANGELOG.rst'), 'r', 'utf8').read()
    old_tag = ".. Omit older changes from package"
    changelog_body_end = changelog.index(old_tag)
    assert changelog_body_end
    changelog_body = changelog[:changelog_body_end]

    bars = '=' * len(title)
    long_description = """
%(bars)s
%(title)s
%(bars)s
%(readme_body)s

%(changelog_body)s

_(Older changes can be found in the full documentation)._
""" % locals()
    return long_description


setup(
    name='django-pylibmc',
    version=django_pylibmc.__version__,
    description='Django cache backend using pylibmc',
    long_description=get_long_description('django-pylibmc'),
    author='Jeff Balogh',
    author_email='jbalogh@mozilla.com',
    url='https://github.com/django-pylibmc/django-pylibmc',
    license='BSD',
    packages=['django_pylibmc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['pylibmc>=1.4.1'],
    tests_require=['tox'],
    cmdclass={'test': Tox},
    keywords='django cache pylibmc memcached',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        # I don't know what exactly this means, but why not?
        'Environment :: Web Environment :: Mozilla',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
