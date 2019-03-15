#!/usr/bin/env python

import sys
from os.path import join, dirname

from setuptools import setup, find_packages

DESCRIPTION = """
 SPPLibrary is the automation framework for the HP SPP Product.
 This library is dependent on the RoboGalaxyLibrary core.
 """[1:-1]

setup(name='SppLibrary',
      version='1.0',
      description='Web, API and CLI testing library for Robot Framework',
      long_description=DESCRIPTION,
      author='SPP Automation Team',
      author_email='<CSI_SPP_Automation@groups.ext.hpe.com>',
      url='',
      keywords='robotframework robogalaxy robogalaxylibrary SppLibrary',
      platforms='any',
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Testing"
      ],
      install_requires=[
          'RoboGalaxyLibrary >= 0.94',
          'WMI >= 1.4.9',
          'xlrd >= 0.7.1',
          'BeautifulSoup4 >= 4.4.0',
          'html5lib >= 1.0b8'
      ],
      packages=find_packages()
      )
