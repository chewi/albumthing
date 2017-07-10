# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib, GdkPixbuf
from xmmsclient import collections as xc
import xmmsclient
import operator
from .albumthing import AlbumThing
from .coverart import CoverArt
from . import const
from functools import partial
from .coverartfetcher import CoverArtFetcher


class AlbumListThing(Gtk.VBox):
    def __init__(self):
        super(AlbumListThing, self).__init__(homogeneous=False, spacing=4)

        self.__at = AlbumThing()

        self.filter_entry = Gtk.Entry()
        self.pack_start(self.filter_entry, False, True, 0)

        self.album_list = AlbumList()

        scrolled_album = Gtk.ScrolledWindow()
        scrolled_album.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_album.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_album.add(self.album_list)
        self.pack_start(scrolled_album, True, True, 0)

        self.filter_entry.connect('changed', self.__gtk_cb_changed, None)


    def __xmms_cb_medialib_entry_added(self, result):
        print('added %s' % result.value())


    def __xmms_cb_medialib_entry_changed(self, result):
        print('changed %s' % result.value())


    def __gtk_cb_changed(self, editable, user_data):
        self.refresh()


    def setup_callbacks(self):
        self.album_list.setup_callbacks()
        self.__at.xmms.broadcast_medialib_entry_added(
                cb=self.__xmms_cb_medialib_entry_added)
        self.__at.xmms.broadcast_medialib_entry_changed(
                cb=self.__xmms_cb_medialib_entry_changed)


    def refresh(self):
        text = self.filter_entry.get_text()
        self.album_list.filter('*' + text + '*' if text else None)


class AlbumList(Gtk.TreeView):
    def __init__(self):
        super(AlbumList, self).__init__()

        self.__at = AlbumThing()

        self.set_headers_visible(False)
        self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        self.list_store = Gtk.ListStore(GdkPixbuf.Pixbuf,
                                        GObject.TYPE_STRING,
                                        GObject.TYPE_PYOBJECT)

        self.pixbuf_renderer = Gtk.CellRendererPixbuf()
        self.pixbuf_renderer.set_fixed_size(-1, const.COVER_SIZE + 4)
        self.text_renderer = Gtk.CellRendererText()

        self.cover_column = Gtk.TreeViewColumn('cover')
        self.cover_column.pack_start(self.pixbuf_renderer, True)
        self.cover_column.add_attribute(self.pixbuf_renderer, 'pixbuf', 0)
        self.append_column(self.cover_column)

        self.name_column = Gtk.TreeViewColumn('name')
        self.name_column.pack_start(self.text_renderer, True)
        self.name_column.add_attribute(self.text_renderer, 'markup', 1)
        self.append_column(self.name_column)

        self.set_model(self.list_store)

        self.get_selection().connect('changed',
                self.__gtk_cb_selection_changed, None)


    def __xmms_cb_song_list(self, sresult, aresults):
        self.__at.cover_art_fetcher.reset()
        self.list_store.clear()
        self.columns_autosize()

        tracks = sresult['tracks']

        if tracks:
            secs = sresult['duration'] / 1000
            mins, secs = divmod(secs, 60)

            iter = self.list_store.append(
                [None, '<b>%s</b>\nVarious Artists <small>- %d Tracks/%d:%02d Minutes</small>' %
                 (const.UNKNOWN, len(tracks), mins, secs), tracks]
            )

            if self.__at.configuration.get('ui', 'show_cover_art'):
                self.list_store.set_value(iter, 0, CoverArt.fallback)

        for r in sorted(aresults, key=lambda r: r['album'].lower()):
            secs = r['duration'] / 1000
            mins, secs = divmod(secs, 60)

            album = GLib.markup_escape_text(r['album'] or const.UNKNOWN)
            artist = GLib.markup_escape_text(r['artist'] or const.UNKNOWN)
            tracks = r['tracks']

            iter = self.list_store.append(
                [None, '<b>%s</b>\n%s <small>- %d Tracks/%d:%02d Minutes</small>' %
                 (album, artist, len(tracks), mins, secs), tracks]
            )

            if self.__at.configuration.get('ui', 'show_cover_art'):
                if r['cover_art']:
                    self.__at.cover_art_fetcher.fetch_async(r['cover_art'], partial(self.set_cover, iter))
                else:
                    self.list_store.set_value(iter, 0, CoverArt.fallback)


    def __xmms_cb_playback_status(self, result):
        if result.value() == xmmsclient.PLAYBACK_STATUS_STOP and \
                self.__at.configuration.get('behaviour', 'random_album'):
            self.__at.win.playlist.playlist.start_playback = True
            self.random_album()


    def __gtk_cb_selection_changed(self, selection, user_data):
       (model, rows) = selection.get_selected_rows()

       if not rows:
           # FIXME: What should we do?
           return

       tracks = []

       for path in rows:
           iter = self.list_store.get_iter(path)
           tracks.extend(self.list_store.get_value(iter, 2))

       self.__at.win.playlist.load_tracks(tracks)


    def set_cover(self, iter, result):
        cover_art = CoverArt(result, const.COVER_SIZE)
        self.list_store.set_value(iter, 0, cover_art.pixbuf)


    def filter(self, string):
        if not string:
            coll = xc.Universe()
        else:
            coll_artist = xc.Match(field='artist', value=string)
            coll_album = xc.Match(field='album', value=string)
            coll_title = xc.Match(field='title', value=string)
            coll = xc.Union(coll_artist, coll_album, coll_title)

        scoll = xc.Order(xc.Order(coll, 'title'), 'artist')
        acoll = xc.Order(xc.Order(xc.Order(coll, 'tracknr'), 'partofset'), 'album_artist_sort')

        sresult = self.__at.xmms.coll_query(
            xc.Intersection(scoll, xc.Complement(xc.Has(field='album'))),
            {
                'type': 'organize',
                'data': {
                    'duration': {
                        'type': 'metadata',
                        'get': ['value'],
                        'fields': ['duration'],
                        'aggregate': 'sum'
                    },
                    'tracks': {
                        'type': 'metadata',
                        'get': ['id'],
                        'aggregate': 'set'
                    }
                }
            }
        )

        cluster_data = {
            'type': 'organize',
            'data': {
                'artist': {
                    'type': 'metadata',
                    'get': ['value'],
                    'fields': ['album_artist', 'artist']
                },
                'album': {
                    'type': 'metadata',
                    'get': ['value'],
                    'fields': ['album']
                },
                'cover_art': {
                    'type': 'metadata',
                    'get': ['value'],
                    'fields': ['picture_front']
                },
                'duration': {
                    'type': 'metadata',
                    'get': ['value'],
                    'fields': ['duration'],
                    'aggregate': 'sum'
                },
                'tracks': {
                    'type': 'metadata',
                    'get': ['id'],
                    'aggregate': 'set'
                }
            }
        }

        aresult = self.__at.xmms.coll_query(
            xc.Intersection(acoll, xc.Complement(xc.Has(field='album_id'))),
            {
                'type': 'cluster-list',
                'cluster-field': 'album',
                'data': cluster_data
            }
        )

        aidresult = self.__at.xmms.coll_query(
            xc.Intersection(acoll, xc.Has(field='album')),
            {
                'type': 'cluster-list',
                'cluster-field': 'album_id',
                'data': cluster_data
            }
        )

        sresult.wait()
        aresult.wait()
        aidresult.wait()

        self.__xmms_cb_song_list(sresult.value(), aresult.value() + aidresult.value())


    def random_album(self):
        import random

        r = random.randint(0, self.list_store.iter_n_children(None))
        self.get_selection().unselect_all()
        self.get_selection().select_iter(
                self.list_store.get_iter_from_string('%d:' % r))
        self.scroll_to_cell('%d:' % r)


    def setup_callbacks(self):
        self.filter(None)
        self.__at.xmms.broadcast_playback_status(
                cb=self.__xmms_cb_playback_status)
