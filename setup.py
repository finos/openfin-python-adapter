import os
import os.path
import io
from setuptools import setup, find_packages
    
VERSION = "0.1.0"
here = os.path.abspath(os.path.dirname(__file__))

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python',
    'Topic :: Software Development',
]

setup(
    # Version
    version=VERSION,

    # Info
    name='openfin',
    description='Python Openfin adapter.',
    url='https://github.com/jpmorganchase/openfin-python-adapter',
    
    # Author Info
    author='Luke Sheard',
    author_email='luke.sheard@jpmorgan.com',
    
    # PyPi Info
    classifiers=CLASSIFIERS,

    install_requires=[
        "tornado==4.4.1"
    ],

    extras_require={
        ':sys_platform == "win32"': [
            'pywin32',
            'pyreadline'
        ],
    },

    # Packaging
    packages=['openfin', 'openfin.api', 'openfin.backends', 'openfin.backends.tornado', 'openfin.utils']
)