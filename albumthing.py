#!/usr/bin/env python
#
# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


from AlbumThing.albumthing import AlbumThing
import gtk
from AlbumThing import albumwindow



if __name__ == '__main__':
    AlbumThing()

    win = albumwindow.AlbumWindow()
    gtk.main()
