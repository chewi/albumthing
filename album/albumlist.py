import pygtk
pygtk.require('2.0')
import gtk
import gobject
from collections import deque


COVER_SIZE = 64


class AlbumList(gtk.TreeView):
    def __init__(self, xmms):
        super(AlbumList, self).__init__()

        self.xmms = xmms
        self.ids = 0
        self.picture_queue = deque()

        self.set_headers_visible(False)

        self.list_store = gtk.ListStore(gtk.gdk.Pixbuf,
                gobject.TYPE_STRING, gobject.TYPE_INT)

        self.pixbuf_renderer = gtk.CellRendererPixbuf()
        self.pixbuf_renderer.set_fixed_size(-1, COVER_SIZE + 4)
        self.text_renderer = gtk.CellRendererText()

        self.cover_column = gtk.TreeViewColumn('cover')
        self.cover_column.pack_start(self.pixbuf_renderer, True)
        self.cover_column.add_attribute(self.pixbuf_renderer, 'pixbuf', 0)
        self.append_column(self.cover_column)

        self.name_column = gtk.TreeViewColumn('name')
        self.name_column.pack_start(self.text_renderer)
        self.name_column.add_attribute(self.text_renderer, 'markup', 1)
        self.append_column(self.name_column)

        self.set_model(self.list_store)


    def __increase_ids(self):
        self.ids = self.ids + 1


    def add_album(self, album):
        """
        Adds an Album to the list
        """

        def __bindata_retrieve(result):
            pixbuf_loader = gtk.gdk.PixbufLoader()
            pixbuf_loader.write(result.get_bin())
            pixbuf_loader.close()
            try:
                id = self.picture_queue.pop ()
            except IndexError:
                return
            self.set_cover(id, pixbuf_loader.get_pixbuf())

        # FIXME: Escape album name, etc.
        self.list_store.append([None, '<b>%s</b>\n%s <small>- %d Tracks/%d:%02d Minutes</small>' % (album.name, album.artist, album.size, album.get_duration_min(), album.get_duration_sec()), self.ids])

        if album.picture_front:
            self.picture_queue.appendleft(self.ids)
            self.xmms.bindata_retrieve(album.picture_front,
                    cb=__bindata_retrieve)

        self.__increase_ids()


    def set_cover(self, id, pixbuf):
        if not pixbuf:
            return

        pixbuf = pixbuf.scale_simple(COVER_SIZE, COVER_SIZE,
                gtk.gdk.INTERP_BILINEAR)

        iter = self.list_store.get_iter_first()
        while iter:
            if id == self.list_store.get_value(iter, 2):
                self.list_store.set_value(iter, 0, pixbuf)
                break
            iter = self.list_store.iter_next(iter)
