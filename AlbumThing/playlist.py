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


class PlayListThing(gtk.VBox):
    def __init__(self):
        super(PlayListThing, self).__init__(homogeneous=False, spacing=4)

        self.__at = AlbumThing()

        self.__active = None

        self.active_playlist_button = gtk.Button(_('Show active playlist'),
                gtk.STOCK_GO_BACK)
        self.active_playlist_button.set_relief(gtk.RELIEF_NONE)
        self.pack_start(self.active_playlist_button, expand=False)

        self.playlist = PlayList()

        scrolled_playlist = gtk.ScrolledWindow()
        scrolled_playlist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_playlist.set_shadow_type(gtk.SHADOW_IN)
        scrolled_playlist.add(self.playlist)
        self.pack_start(scrolled_playlist)

        self.active_playlist_button.connect('clicked',
                self.__gtk_cb_button_clicked, None)


    def __xmms_cb_playlist_current_active(self, result):
        self.__active = result.value()
        self.active_playlist_button.hide()


    def __xmms_cb_current_pos(self, result):
        self.__at.xmms.playlist_current_active(
                cb=self.__xmms_cb_playlist_current_active)


    def __gtk_cb_button_clicked(self, button, user_data):
        self.recover_active()


    def load_coll(self, coll):
        if self.__active == const.PLAYLIST_NAME1:
            pls = const.PLAYLIST_NAME2
        else:
            pls = const.PLAYLIST_NAME1
        self.__at.xmms.playlist_clear(pls)
        self.__at.xmms.playlist_add_collection(coll, order=['album', 'tracknr'],
                playlist=pls)
        self.__at.xmms.playlist_load(pls)

        self.active_playlist_button.show()


    def recover_active(self):
        self.active_playlist_button.hide()
        self.__at.xmms.playlist_load(self.__active)


    def setup_callbacks(self):
        self.playlist.setup_callbacks()
        self.__at.xmms.playlist_current_active(
                cb=self.__xmms_cb_playlist_current_active)
        self.__at.xmms.broadcast_playlist_current_pos(
                cb=self.__xmms_cb_current_pos)


class PlayList(gtk.TreeView):
    def __init__(self):
        super(PlayList, self).__init__()

        self.__at = AlbumThing()
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
        self.__insert_media_info_result(-1, result)

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
            self.insert_entry_by_id(res['position'], res['id'])
        elif res['type'] == xmmsclient.PLAYLIST_CHANGED_REMOVE:
            self.remove_entry(res['position'])
        elif res['type'] == xmmsclient.PLAYLIST_CHANGED_CLEAR:
            self.list_store.clear()
        elif res['type'] == xmmsclient.PLAYLIST_CHANGED_MOVE:
            self.move_entry(res['position'], res['newposition'])
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
        p1 = False
        p2 = False
        for playlist in result.value():
            if playlist == const.PLAYLIST_NAME1:
                p1 = True
            elif playlist == const.PLAYLIST_NAME2:
                p2 = True

        if not p1:
            self.__at.xmms.playlist_create(const.PLAYLIST_NAME1)
        if not p2:
            self.__at.xmms.playlist_create(const.PLAYLIST_NAME2)


    def __gtk_cb_row_activated(self, treeview, path, column, user_data):
        self.__at.xmms.playlist_set_next(path[0])
        self.__at.xmms.playback_start()
        self.__at.xmms.playback_tickle()


    def __insert_media_info_result(self, pos, result):
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
        self.insert_entry(pos, result.value()['id'], artist, title, album)


    def insert_entry(self, pos, id, artist, title, album):
        self.list_store.insert(pos, [None,
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


    def move_entry(self, pos, new_pos):
        iter_old = self.list_store.get_iter_from_string('%d:' % pos)
        iter_new = self.list_store.get_iter_from_string('%d:' % new_pos)
        self.list_store.move_after(iter_old, iter_new)


    def set_active(self, pos):
        i = 0
        iter = self.list_store.get_iter_first()
        while iter:
            self.list_store.set_value(iter, 0, None)
            if pos == i:
                self.list_store.set_value(iter, 0, self.__status)
            i = i + 1
            iter = self.list_store.iter_next(iter)


    def insert_entry_by_id(self, pos, id):
        def xmms_cb_id_info(result):
            self.__insert_media_info_result(pos, result)

        self.__at.xmms.medialib_get_info(id, cb=xmms_cb_id_info)


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
