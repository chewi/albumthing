#!/usr/bin/env python
#
# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import gtk
import gettext
from AlbumThing.albumthing import AlbumThing
from AlbumThing import albumwindow


if __name__ == '__main__':
    gettext.install('albumthing')

    AlbumThing()

    win = albumwindow.AlbumWindow()
    gtk.main()
