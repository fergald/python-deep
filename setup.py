#!/usr/bin/python

from distutils.core import setup

setup(name='deep',
      version='0.9.dev',
      packages = ['deep'],
      author="Fergal Daly",
      author_email="fergal@esatclear.ie",
      install_requires=['six'],
      description="Easy, flexible deep comparison and testing of structured data",
      url="http://code.google.com/p/python-deep/",
      download_url="http://code.google.com/p/python-deep/downloads/list",
      license="LGPL",
      )
