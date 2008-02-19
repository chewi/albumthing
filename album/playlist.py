import pygtk
pygtk.require('2.0')
import gtk
import gobject
import xmmsclient


class PlayList(gtk.TreeView):
    def __init__(self, xmms):
        super(PlayList, self).__init__()

        self.__xmms = xmms
        self.__status = gtk.STOCK_MEDIA_STOP
        self.__playlist_pos = 0

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
            try:
                artist = result.value()['artist']
            except KeyError:
                artist = 'Unknown'
            try:
                title = result.value()['title']
            except KeyError:
                title = 'Unknown (%s)' % result.value()['url']
            self.add_entry(result.value()['id'], artist, title)

        def entry_list(result):
            self.list_store.clear()
            for id in result.value():
                self.__xmms.medialib_get_info(id, cb=id_info)
            self.__xmms.playlist_current_pos(cb=current_pos)
            self.__xmms.broadcast_playlist_current_pos(cb=current_pos)
            self.__xmms.playback_status(cb=playback_status)
            self.__xmms.broadcast_playback_status(cb=playback_status)

        def current_pos(result):
            self.__playlist_pos = result.value()
            self.set_active(result.value())

        def playlist_loaded(result):
            self.__xmms.playlist_list_entries(cb=entry_list)

        def playlist_changed(result):
            res = result.value()
            if res['type'] == xmmsclient.PLAYLIST_CHANGED_ADD:
                self.__xmms.medialib_get_info(res['id'], cb=id_info)
            elif res['type'] == xmmsclient.PLAYLIST_CHANGED_INSERT:
                # FIXME: How do we remember the playlist position upon getting
                #        the media info?
                pass
            elif res['type'] == xmmsclient.PLAYLIST_CHANGED_REMOVE:
                self.remove_entry(res['position'])
            elif res['type'] == xmmsclient.PLAYLIST_CHANGED_CLEAR:
                self.list_store.clear()
            elif res['type'] == xmmsclient.PLAYLIST_CHANGED_MOVE:
                # FIXME: Let's see
                pass
            elif res['type'] == xmmsclient.PLAYLIST_CHANGED_SORT:
                self.__xmms.playlist_list_entries(cb=entry_list)
            elif res['type'] == xmmsclient.PLAYLIST_CHANGED_SHUFFLE:
                self.__xmms.playlist_list_entries(cb=entry_list)

        def playback_status(result):
            status = result.value()
            if status == xmmsclient.PLAYBACK_STATUS_PAUSE:
                self.__status = gtk.STOCK_MEDIA_PAUSE
            elif status == xmmsclient.PLAYBACK_STATUS_PLAY:
                self.__status = gtk.STOCK_MEDIA_PLAY
            elif status == xmmsclient.PLAYBACK_STATUS_STOP:
                self.__status = gtk.STOCK_MEDIA_STOP
            self.set_active(self.__playlist_pos)

        self.__xmms.playlist_create('_album')

        self.__xmms.playlist_list_entries(cb=entry_list)
        self.__xmms.broadcast_playlist_loaded(cb=playlist_loaded)
        self.__xmms.broadcast_playlist_changed(cb=playlist_changed)

        def row_activated(treeview, path, column, user_data):
            self.__xmms.playlist_set_next(path[0])
            self.__xmms.playback_start()
            self.__xmms.playback_tickle()

        self.connect('row-activated', row_activated, None)


    def add_entry(self, id, artist, title):
        # FIXME: Escape album name, etc.
        self.list_store.append([None, '<b>%s</b>\n%s' % (title, artist), id])


    def remove_entry(self, pos):
        i = 0
        iter = self.list_store.get_iter_first()
        while iter:
            if pos == i:
                self.list_store.remove(iter)
                break
            i = i + 1
            iter = self.list_store.iter_next(iter)


    def set_active(self, pos):
        i = 0
        iter = self.list_store.get_iter_first()
        while iter:
            self.list_store.set_value(iter, 0, None)
            if pos == i:
                self.list_store.set_value(iter, 0, self.__status)
            i = i + 1
            iter = self.list_store.iter_next(iter)
