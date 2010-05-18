from setuptools import setup

import django_pylibmc


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
    install_requires=['pylibmc', 'Django>=1.2'],
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
