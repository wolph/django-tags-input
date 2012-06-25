import tags_input
import os
from setuptools import setup

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ('See http://pypi.python.org/pypi/'
        + tags_input.__name__)

setup(
    name=tags_input.__name__,
    version=tags_input.__version__,
    author=tags_input.__author__,
    author_email=tags_input.__author_email__,
    description=tags_input.__description__,
    url=tags_input.__url__,
    license='BSD',
    packages=['tags_input'],
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
    setup_requires=['nose'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)

