#!/usr/bin/env python

import setuptools
from verwatch.core import VERSION

setuptools.setup(
    name='verwatch',
    version=VERSION,
    description='Package version watch utility',
    author='Jakub Ruzicka',
    author_email='jruzicka@redhat.com',
    #url='http://',
    #packages=['distutils', 'distutils.command'],
    entry_points={
        "console_scripts": ["verw = verwatch.shell:main"]
    }
    )
