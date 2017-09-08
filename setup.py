import os
import sys
import setuptools
from setuptools.command.test import test as TestCommand


# To prevent importing about and thereby breaking the coverage info we use this
# exec hack
about = {}
with open('tags_input/__about__.py') as fp:
    exec(fp.read(), about)


if os.path.isfile('README.rst'):
    with open('README.rst') as fh:
        readme = fh.read()
else:
    readme = \
        'See http://pypi.python.org/pypi/%(__package_name__)s/' % about


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
    name=about['__package_name__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__email__'],
    description=about['__description__'],
    url=about['__url__'],
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
    long_description=readme,
    cmdclass={'test': PyTest},
    classifiers=['License :: OSI Approved :: BSD License'],
    install_requires=[
        'six',
    ]
)

