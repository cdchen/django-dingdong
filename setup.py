# -*- coding: utf-8 -*-
import sys
import os

project_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(project_dir, 'src'))

import django_dingdong

version = django_dingdong.version

install_requires = [
    'django>=1.6,<1.7',
    'south',
    'django-extensions',
    'django-suit',
    'django-model-report',
    'django_nose',
    'django-polymorphic',
    'celery',
    'django-celery',
    'djangorestframework',
    'sphinxcontrib-httpdomain',
    'django-markwhat',
    'django-rest-swagger',
    'django-filter',
    'markdown',
    'django-enumfield',
    'shortuuid',
    'sphinx_rtd_theme',
]

setup_requires = [
]

dependency_links = [
]

license = open('LICENSE.txt').read()
long_description = open('README.rst').read()

from setuptools import setup, find_packages

setup(
    name='django-dingdong',
    version=version,
    description="",
    long_description=long_description,
    author='niceStudio',
    author_email='',
    url='',
    license=license,
    packages=find_packages('src', exclude=['docs', 'tests']),
    package_dir={
        '': 'src'
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
)


