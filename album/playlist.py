import pygtk
pygtk.require('2.0')
import gtk
import gobject


class PlayList(gtk.TreeView):
    def __init__(self, xmms):
        super(PlayList, self).__init__()

        self.__xmms = xmms

        self.set_headers_visible(False)

        self.list_store = gtk.ListStore(gtk.gdk.Pixbuf,
                gobject.TYPE_STRING, gobject.TYPE_INT)

        self.pixbuf_renderer = gtk.CellRendererPixbuf()
        self.text_renderer = gtk.CellRendererText()

        self.status_column = gtk.TreeViewColumn('status')
        self.status_column.pack_start(self.pixbuf_renderer, True)
        self.status_column.add_attribute(self.pixbuf_renderer, 'stock-id', 0)
        self.append_column(self.status_column)

        self.name_column = gtk.TreeViewColumn('name')
        self.name_column.pack_start(self.text_renderer)
        self.name_column.add_attribute(self.text_renderer, 'markup', 1)
        self.append_column(self.name_column)

        self.set_model(self.list_store)
