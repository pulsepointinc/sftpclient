#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='pp-sftpclient',
    version='1.0.2',
    description='Wrapper for some SFTP clients',
    author='erachitskiy',
    author_email='erachitskiy@pulsepoint.com',
    url='https://github.com/pulsepointinc/sftpclient',
    packages=find_packages(),
    install_requires=[
        'paramiko',
        'sftpserver',
        'ssh2-python',
    ],
    extras_require={
        'test': [
            'pytest',
            'six',
        ]
    },
    zip_safe=False,
)
