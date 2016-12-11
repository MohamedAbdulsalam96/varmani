# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(
    name='varmani',
    version=version,
    description='Varmani Network Management Application',
    author='Hemant Pema',
    author_email='hem@varmani.co.za',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
