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


long_description = "\n".join(
    [open(f).read() for f in ['README.rst', 'CHANGELOG.rst']])

setup(
    name='django-pylibmc',
    version=django_pylibmc.__version__,
    description='Django cache backend using pylibmc',
    long_description=long_description,
    author='Jeff Balogh',
    author_email='jbalogh@mozilla.com',
    url='https://github.com/django-pylibmc/django-pylibmc',
    license='BSD',
    packages=['django_pylibmc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['pylibmc>=1.4.1', 'Django>=1.4'],
    tests_require=['tox'],
    cmdclass = {'test': Tox},
    keywords = 'django cache pylibmc memcached',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        # I don't know what exactly this means, but why not?
        'Environment :: Web Environment :: Mozilla',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
