# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk


class CoverArt:
    def __init__(self, data, size):
        pixbuf_loader = gtk.gdk.PixbufLoader()
        self.pixbuf = None

        try:
            pixbuf_loader.write(data)
            pixbuf_loader.close()
            self.pixbuf = pixbuf_loader.get_pixbuf()
        except Exception, detail:
            # FIXME: Better use an own icon
            widget = gtk.Image()
            self.pixbuf = widget.render_icon(gtk.STOCK_CDROM, gtk.ICON_SIZE_DND)

        self.pixbuf = self.pixbuf.scale_simple(size, size,
                gtk.gdk.INTERP_BILINEAR)
