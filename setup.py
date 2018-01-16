#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='sftpclient',
      version='1.0.0',
      description='Wrapper for some SFTP clients',
      author='erachitskiy',
      author_email='erachitskiy@pulsepoint.com',
      url='https://github.com/pulsepointinc/sftpclient',
      packages=find_packages(),
      install_requires = [
            'ssh2-python>=0.8.0',
            'paramiko>=2.3.1'
      ],
      zip_safe=False
      )