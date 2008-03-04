# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk
import gobject
from gobject import markup_escape_text
from xmmsclient import collections as xc
import operator
from album import Album
from albumthing import AlbumThing


COVER_SIZE = 40


class AlbumListThing(gtk.VBox):
    def __init__(self):
        super(AlbumListThing, self).__init__(homogeneous=False, spacing=4)

        self.__at = AlbumThing ()

        self.filter_entry = gtk.Entry()
        self.pack_start(self.filter_entry, expand=False)

        self.album_list = AlbumList()

        scrolled_album = gtk.ScrolledWindow()
        scrolled_album.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_album.set_shadow_type(gtk.SHADOW_IN)
        scrolled_album.add(self.album_list)
        self.pack_start(scrolled_album)

        self.filter_entry.connect('changed', self.__gtk_cb_changed, None)


    def __xmms_cb_medialib_entry_added(self, result):
        print 'added %s' % result.value()


    def __xmms_cb_medialib_entry_changed(self, result):
        print 'changed %s' % result.value()


    def __gtk_cb_changed(self, editable, user_data):
        self.refresh()


    def setup_callbacks(self):
        self.album_list.setup_callbacks()
        self.__at.xmms.broadcast_medialib_entry_added(
                cb=self.__xmms_cb_medialib_entry_added)
        self.__at.xmms.broadcast_medialib_entry_changed(
                cb=self.__xmms_cb_medialib_entry_changed)


    def refresh(self):
        self.album_list.filter(self.filter_entry.get_text())


class AlbumList(gtk.TreeView):
    def __init__(self):
        super(AlbumList, self).__init__()

        self.__ids = 0
        self.__at = AlbumThing ()

        self.set_headers_visible(False)
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        self.list_store = gtk.ListStore(gtk.gdk.Pixbuf,
                gobject.TYPE_STRING, gobject.TYPE_INT,
                gobject.TYPE_STRING, gobject.TYPE_STRING)

        self.pixbuf_renderer = gtk.CellRendererPixbuf()
        self.pixbuf_renderer.set_fixed_size(-1, COVER_SIZE + 4)
        self.text_renderer = gtk.CellRendererText()

        self.cover_column = gtk.TreeViewColumn('cover')
        self.cover_column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.cover_column.pack_start(self.pixbuf_renderer, True)
        self.cover_column.add_attribute(self.pixbuf_renderer, 'pixbuf', 0)
        self.append_column(self.cover_column)

        self.name_column = gtk.TreeViewColumn('name')
        self.name_column.pack_start(self.text_renderer)
        self.name_column.add_attribute(self.text_renderer, 'markup', 1)
        self.append_column(self.name_column)

        self.set_model(self.list_store)
        self.set_search_column(4)

        self.get_selection().connect('changed',
                self.__gtk_cb_selection_changed, None)


    def __xmms_cb_song_list(self, result):
        self.list_store.clear()
        duration = 0
        last_album = None
        last_artist = None
        album = None
        songs = result.value()
        songs.sort(key=operator.itemgetter('album', 'artist'))
        for song in songs:
            if album and last_album == song['album'] and \
                    last_artist == song['artist']:
                album.increase_size()
                album.add_duration(song['duration'])
            else:
                if album:
                    self.add_album(album)
                album = Album(self, song['album'],
                        song['artist'], song['picture_front'], 1,
                        song['duration'])

            last_album = song['album']
            last_artist = song['artist']

        self.add_album(album)


    def __gtk_cb_selection_changed(self, selection, user_data):
       (model, rows) = selection.get_selected_rows()

       if not rows:
           # FIXME: What should we do?
           return

       colls = []
       for path in rows:
           iter = self.list_store.get_iter(path)
           artist = self.list_store.get_value(iter, 3)
           album = self.list_store.get_value(iter, 4)
           if not artist and not album:
               colls.append(xc.Intersection(
                   xc.Complement(xc.Has(xc.Universe(), 'artist')),
                   xc.Complement(xc.Has(xc.Universe(), 'album'))))
           elif not artist:
               colls.append(xc.Intersection(
                   xc.Complement(xc.Has(xc.Universe(), 'artist')),
                   xc.Equals(field='album', value=album)))
           elif not album:
               colls.append(xc.Intersection(
                   xc.Complement(xc.Has(xc.Universe(), 'album')),
                   xc.Equals(field='artist', value=artist)))
           else:
               colls.append(xc.Intersection(
                   xc.Equals(field='artist', value=artist),
                   xc.Equals(field='album', value=album)))

       coll = xc.Union(*colls)
       self.__at.xmms.playlist_clear('_album')
       self.__at.xmms.playlist_add_collection(coll, playlist='_album')
       self.__at.xmms.playlist_sort(['tracknr'], playlist='_album')
       self.__at.xmms.playlist_load('_album')


    def __increase_ids(self):
        self.__ids = self.__ids + 1


    def add_album(self, album):
        """
        Adds an Album to the list
        """

        if not album:
            return

        if not album.name:
            name = 'Unknown'
        else:
            name = album.name

        if not album.artist:
            artist = 'Unknown'
        else:
            artist = album.artist

        self.list_store.append([None,
            '<b>%s</b>\n%s <small>- %d Tracks/%d:%02d Minutes</small>' %
            (markup_escape_text(name), markup_escape_text(artist),
                album.size, album.get_duration_min(), album.get_duration_sec()),
            self.__ids, album.artist, album.name])

        album.set_id(self.__ids)
        self.__increase_ids()


    def set_cover(self, id, pixbuf):
        if not pixbuf:
            return

        iter = self.list_store.get_iter_first()
        while iter:
            if id == self.list_store.get_value(iter, 2):
                self.list_store.set_value(iter, 0, pixbuf)
                break
            iter = self.list_store.iter_next(iter)


    def filter(self, string):
        if not string:
            coll = xc.Universe()
        else:
            coll_artist = xc.Match(field='artist', value=string)
            coll_album = xc.Match(field='album', value=string)
            coll_title = xc.Match(field='title', value=string)
            coll = xc.Union(coll_artist, coll_album, coll_title)
        self.__at.xmms.coll_query_infos(coll,
                ['id', 'album', 'artist', 'duration', 'picture_front'],
                cb=self.__xmms_cb_song_list)


    def setup_callbacks(self):
        self.__at.xmms.coll_query_infos(xc.Universe(),
                ['id', 'album', 'artist', 'duration', 'picture_front'],
                cb=self.__xmms_cb_song_list)
