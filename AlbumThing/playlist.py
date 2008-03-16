# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk
import gobject
from gobject import markup_escape_text
import xmmsclient
from albumthing import AlbumThing
import const


class PlayList(gtk.TreeView):
    def __init__(self):
        super(PlayList, self).__init__()

        self.__at = AlbumThing ()
        self.__status = gtk.STOCK_MEDIA_STOP
        self.__playlist_pos = 0

        self.set_headers_visible(False)

        self.list_store = gtk.ListStore(gobject.TYPE_STRING,
                gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING)

        self.pixbuf_renderer = gtk.CellRendererPixbuf()
        self.pixbuf_renderer.set_fixed_size(-1, 32)
        self.text_renderer = gtk.CellRendererText()

        self.status_column = gtk.TreeViewColumn('status')
        self.status_column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.status_column.pack_start(self.pixbuf_renderer, True)
        self.status_column.add_attribute(self.pixbuf_renderer, 'stock-id', 0)
        self.append_column(self.status_column)

        self.name_column = gtk.TreeViewColumn('name')
        self.name_column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.name_column.pack_start(self.text_renderer)
        self.name_column.add_attribute(self.text_renderer, 'markup', 1)
        self.append_column(self.name_column)

        self.set_model(self.list_store)
        self.set_search_column(3)

        self.connect('row-activated', self.__gtk_cb_row_activated, None)


    def __xmms_cb_id_info(self, result):
        if not result.value():
            return

        try:
            artist = result.value()['artist']
        except KeyError:
            artist = const.UNKNOWN
        try:
            title = result.value()['title']
        except KeyError:
            title = '%s (%s)' % (const.UNKNOWN, result.value()['url'])
        try:
            album = result.value()['album']
        except KeyError:
            album = const.UNKNOWN
        self.add_entry(result.value()['id'], artist, title, album)


    def __xmms_cb_entry_list(self, result):
        self.list_store.clear()
        for id in result.value():
            self.__at.xmms.medialib_get_info(id, cb=self.__xmms_cb_id_info)
        self.__at.xmms.playback_status(cb=self.__xmms_cb_playback_status)


    def __xmms_cb_current_pos(self, result):
        self.__playlist_pos = result.value()
        self.set_active(result.value())


    def __xmms_cb_playlist_loaded(self, result):
        self.__at.xmms.playlist_list_entries(cb=self.__xmms_cb_entry_list)


    def __xmms_cb_playlist_changed(self, result):
        res = result.value()
        if res['type'] == xmmsclient.PLAYLIST_CHANGED_ADD:
            self.__at.xmms.medialib_get_info(res['id'],
                    cb=self.__xmms_cb_id_info)
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
            self.__at.xmms.playlist_list_entries(cb=self.__xmms_cb_entry_list)
        elif res['type'] == xmmsclient.PLAYLIST_CHANGED_SHUFFLE:
            self.__at.xmms.playlist_list_entries(cb=self.__xmms_cb_entry_list)


    def __xmms_cb_playback_status(self, result):
        status = result.value()
        if status == xmmsclient.PLAYBACK_STATUS_PAUSE:
            self.__status = gtk.STOCK_MEDIA_PAUSE
        elif status == xmmsclient.PLAYBACK_STATUS_PLAY:
            self.__status = gtk.STOCK_MEDIA_PLAY
        elif status == xmmsclient.PLAYBACK_STATUS_STOP:
            self.__status = gtk.STOCK_MEDIA_STOP
        self.set_active(self.__playlist_pos)
        self.__at.xmms.playlist_current_pos(cb=self.__xmms_cb_current_pos)


    def __xmms_cb_playlist_list(self, result):
        for playlist in result.value():
            if playlist == '_album':
                return
        self.__at.xmms.playlist_create('_album')


    def __gtk_cb_row_activated(self, treeview, path, column, user_data):
        self.__at.xmms.playlist_set_next(path[0])
        self.__at.xmms.playback_start()
        self.__at.xmms.playback_tickle()


    def add_entry(self, id, artist, title, album):
        self.list_store.append([None,
            '<b>%s</b>\n<small>by</small> %s <small>from</small> %s' %
            (markup_escape_text(title), markup_escape_text(artist),
                markup_escape_text(album)), id, title])


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
                break
            i = i + 1
            iter = self.list_store.iter_next(iter)


    def setup_callbacks(self):
        self.__at.xmms.playlist_list(cb=self.__xmms_cb_playlist_list)
        self.__at.xmms.playlist_list_entries(cb=self.__xmms_cb_entry_list)
        self.__at.xmms.broadcast_playlist_loaded(
                cb=self.__xmms_cb_playlist_loaded)
        self.__at.xmms.broadcast_playlist_changed(
                cb=self.__xmms_cb_playlist_changed)
        self.__at.xmms.broadcast_playlist_current_pos(
                cb=self.__xmms_cb_current_pos)
        self.__at.xmms.broadcast_playback_status(
                cb=self.__xmms_cb_playback_status)
