import os

import setuptools

# To prevent importing about and thereby breaking the coverage info we use this
# exec hack
about = {}
with open('tags_input/__about__.py') as fp:
    exec(fp.read(), about)

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ('See http://pypi.python.org/pypi/' +
                        about['__package_name__'])

if __name__ == '__main__':
    setuptools.setup(
        name=about['__package_name__'],
        version=about['__version__'],
        author=about['__author__'],
        author_email=about['__author_email__'],
        description=about['__description__'],
        url=about['__url__'],
        license='BSD',
        packages=setuptools.find_packages(
            exclude=[
                'example',
                'example.*',
            ]
        ),
        package_data={
            'tags_input': [
                'templates/*.html',
                'static/*.min.js',
                'static/*.min.css',
            ],
        },
        extras_require={
            'docs': [
                'django',
                'mock',
                'sphinx>=3.0.0',
            ],
            'tests': [
                'django-utils2>=3.0.0',
                'pytest',
                'pytest-cov',
                'pytest-django',
                'pytest-flake8',
            ],
        },
        long_description=long_description,
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
        ],
    )
