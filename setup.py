#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()

with open('requirements_dev.txt') as requirements_dev_file:
    test_requirements = requirements_dev_file.read().splitlines()

setup(
    name='d8s_python',
    description="Democritus functions for working with Python code.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Floyd Hightower",
    author_email='floyd.hightower27@gmail.com',
    url='https://github.com/democritus-project/d8s-python',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages(exclude=('tests')),
    include_package_data=True,
    install_requires=requirements,
    license="GNU Lesser General Public License v3",
    zip_safe=True,
    keywords="democritus,utility,python,python-asts,python-asts-utility,ast,python-ast,abstract-syntax-tree",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
