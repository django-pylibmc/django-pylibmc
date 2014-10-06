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


setup(
    name='django-pylibmc',
    version=django_pylibmc.__version__,
    description='Django cache backend using pylibmc',
    long_description=open('README.rst').read(),
    author='Jeff Balogh',
    author_email='jbalogh@mozilla.com',
    url='http://github.com/jbalogh/django-pylibmc',
    license='BSD',
    packages=['django_pylibmc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['pylibmc>=1.4.1', 'Django>=1.5,<1.7'],
    tests_require=['tox'],
    cmdclass = {'test': Tox},
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
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
