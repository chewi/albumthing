# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk


CDROM = gtk.Image().render_icon(gtk.STOCK_CDROM, gtk.ICON_SIZE_DND)


class CoverArt:
    def __init__(self, data, size):
        pixbuf_loader = gtk.gdk.PixbufLoader()
        self.pixbuf = None
        global foo

        try:
            pixbuf_loader.write(data)
            pixbuf_loader.close()
            self.pixbuf = pixbuf_loader.get_pixbuf()
            self.pixbuf = self.pixbuf.scale_simple(size, size,
                    gtk.gdk.INTERP_BILINEAR)
        except Exception, detail:
            self.pixbuf = CDROM
