import pygtk
pygtk.require('2.0')
import gtk
import gobject


class PlayList(gtk.TreeView):
    def __init__(self, xmms):
        super(PlayList, self).__init__()

        self.__xmms = xmms

        self.set_headers_visible(False)

        self.list_store = gtk.ListStore(gobject.TYPE_STRING,
                gobject.TYPE_STRING, gobject.TYPE_INT)

        self.pixbuf_renderer = gtk.CellRendererPixbuf()
        self.pixbuf_renderer.set_fixed_size(-1, 32)
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

        def id_info(result):
            self.add_entry(result.value()['id'], result.value()['artist'],
                    result.value()['title'])

        def entry_list(result):
            self.list_store.clear()
            for id in result.value():
                self.__xmms.medialib_get_info(id, cb=id_info)
            self.__xmms.playlist_current_pos(cb=current_pos)
            self.__xmms.broadcast_playlist_current_pos(cb=current_pos)

        def current_pos(result):
            self.set_active(result.value())

        def playlist_loaded(result):
            self.__xmms.playlist_list_entries(cb=entry_list)

        self.__xmms.playlist_list_entries(cb=entry_list)
        self.__xmms.broadcast_playlist_loaded(cb=playlist_loaded)


    def add_entry(self, id, artist, title):
        # FIXME: Escape album name, etc.
        self.list_store.append([None, '<b>%s</b>\n%s' % (title, artist), id])


    def set_active(self, id):
        i = 0
        iter = self.list_store.get_iter_first()
        while iter:
            self.list_store.set_value(iter, 0, None)
            if id == i:
                self.list_store.set_value(iter, 0, gtk.STOCK_MEDIA_PLAY)
            i = i + 1
            iter = self.list_store.iter_next(iter)
