# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib


CDROM = Gtk.Image().render_icon(Gtk.STOCK_CDROM, Gtk.IconSize.DND)


class CoverArt:
    def __init__(self, data, size):
        pixbuf_loader = GdkPixbuf.PixbufLoader()
        self.pixbuf = None
        global foo

        try:
            pixbuf_loader.write(data)
            pixbuf_loader.close()
            self.pixbuf = pixbuf_loader.get_pixbuf()
            self.pixbuf = self.pixbuf.scale_simple(size, size,
                    GdkPixbuf.InterpType.BILINEAR)
        except Exception, detail:
            self.pixbuf = CDROM

        try:
            pixbuf_loader.close()
        except GLib.GError:
            pass
