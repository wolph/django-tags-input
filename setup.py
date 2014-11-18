import os
import setuptools

from tags_input import metadata

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ('See http://pypi.python.org/pypi/'
                        + metadata.__package_name__)

setuptools.setup(
    name=metadata.__package_name__,
    version=metadata.__version__,
    author=metadata.__author__,
    author_email=metadata.__author_email__,
    description=metadata.__description__,
    url=metadata.__url__,
    license='BSD',
    packages=setuptools.find_packages(),
    package_data={
        'tags_input': [
            'templates/*.html',
            'static/js/*.js',
            'static/css/*.css',
            'static/css/base/*.css',
            'static/css/base/images/*.png',
        ],
    },
    long_description=long_description,
    test_suite='nose.collector',
    tests_requires=[
        'Django',
        'pytest',
        'pytest-cache',
        'pytest-cov',
        'pytest-django',
        'pytest-flakes',
        'pytest-pep8',
    ],
    classifiers=['License :: OSI Approved :: BSD License'],
)

