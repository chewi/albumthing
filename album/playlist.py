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

        def id_info(result):
            self.add_entry(result.value()['id'], result.value()['artist'],
                    result.value()['title'])

        def entry_list(result):
            for id in result.value():
                self.__xmms.medialib_get_info(id, cb=id_info)

        def current_pos(result):
            print '\n\n\n\n\n' + result.value() + '\n\n\n\n\n'

        self.__xmms.playlist_list_entries(cb=entry_list)
        self.__xmms.broadcast_playlist_current_pos(cb=current_pos)


    def add_entry(self, id, artist, title):
        # FIXME: Escape album name, etc.
        self.list_store.append([None, '<b>%s</b>\n%s' % (title, artist), id])
