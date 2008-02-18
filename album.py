#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import xmmsclient
from xmmsclient import glib as xmmsglib
import sys
import os
from album import albumwindow


if __name__ == '__main__':
    xmms = xmmsclient.XMMS('album')
    try:
        xmms.connect(os.getenv('XMMS_PATH'))
    except IOError, detail:
        print 'Connection failed: %s' % detail
        sys.exit(1)

    conn = xmmsglib.GLibConnector(xmms)

    win = albumwindow.AlbumWindow(xmms)
    gtk.main()
