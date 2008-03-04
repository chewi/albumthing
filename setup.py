#!/usr/bin/env python

from distutils.core import setup


setup(name='AlbumThing',
      version='0.1',
      description='A simple XMMS2 client',
      author='Sebastian Sareyko',
      url='http://nooms.de/',
      packages=['AlbumThing'],
      scripts=['albumthing.py'],
      data_files=[('share/applications', ['data/AlbumThing.desktop'])],
      )
