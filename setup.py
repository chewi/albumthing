#!/usr/bin/env python

from distutils.core import setup
from glob import glob
import os
from AlbumThing import const


NAME = const.NAME
DATA_FILES = [('share/applications', ['data/AlbumThing.desktop'])]

for f in glob('po/*.po'):
    filename, ext = os.path.splitext(f)
    lang = os.path.basename(filename)
    try:
        os.makedirs('po/%s' % lang)
    except OSError:
        pass
    os.system('msgfmt %s -o %s/albumthing.mo' % (f, filename))
    DATA_FILES += [('share/locale/%s/LC_MESSAGES' % lang,
        ['po/%s/albumthing.mo' % lang])]

setup(name=NAME,
      version=const.VERSION,
      description=const.DESC,
      author='Sebastian Sareyko',
      url=const.URL,
      packages=['AlbumThing'],
      scripts=['albumthing.py'],
      data_files=DATA_FILES,
      )
