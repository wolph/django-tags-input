import os
import sys
import setuptools
from setuptools.command.test import test as TestCommand

from tags_input import metadata

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ('See http://pypi.python.org/pypi/' +
                        metadata.__package_name__)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setuptools.setup(
    name=metadata.__package_name__,
    version=metadata.__version__,
    author=metadata.__author__,
    author_email=metadata.__author_email__,
    description=metadata.__description__,
    url=metadata.__url__,
    license='BSD',
    packages=setuptools.find_packages(exclude=[
        'example',
        'example.*',
    ]),
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
    cmdclass={'test': PyTest},
    classifiers=['License :: OSI Approved :: BSD License'],
    install_requires=[
        'six',
    ]
)

