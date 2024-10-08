#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'netCDF4',
    'numpy>=1.14.0',
    'beautifulsoup4',
    'requests',
    'packaging'
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
    'bump2version',
    'wheel',
    'watchdog',
    'ruff',
    'coverage',
    'Sphinx',
    'twine',
    'pydata-sphinx-theme',
    'sphinx_mdinclude',
]

setup(
    author="The pyfar developers",
    author_email='info@pyfar.org',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    description="Maybe the most complete python package for SOFA files so far",
    install_requires=requirements,
    license="MIT license",
    long_description_content_type='text/markdown',
    long_description=readme,
    include_package_data=True,
    keywords='sofar',
    name='sofar',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url="https://pyfar.org/",
    download_url="https://pypi.org/project/sofar/",
    project_urls={
        "Bug Tracker": "https://github.com/pyfar/sofar/issues",
        "Documentation": "https://sofar.readthedocs.io/",
        "Source Code": "https://github.com/pyfar/sofar",
    },
    version='1.2.0',
    zip_safe=False,
    python_requires='>=3.8',
)
