import jquery_tags_input
import os
from setuptools import setup

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ('See http://pypi.python.org/pypi/'
        'django-jquery-tags-input/')

setup(
    name='django-jquery-tags-input',
    version=jquery_tags_input.__version__,
    author=jquery_tags_input.__author__,
    author_email=jquery_tags_input.__author_email__,
    description=jquery_tags_input.__description__,
    url='https://github.com/WoLpH/django-jquery-tags-input',
    license='BSD',
    packages=['jquery_tags_input'],
    long_description=long_description,
    test_suite='nose.collector',
    setup_requires=['nose'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)

