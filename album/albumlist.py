import pygtk
pygtk.require('2.0')
import gtk
import gobject
from xmmsclient import collections as xc
import operator
from album import Album


COVER_SIZE = 40


class AlbumList(gtk.TreeView):
    def __init__(self, xmms):
        super(AlbumList, self).__init__()

        self.__xmms = xmms
        self.__ids = 0

        self.set_headers_visible(False)
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        self.list_store = gtk.ListStore(gtk.gdk.Pixbuf,
                gobject.TYPE_STRING, gobject.TYPE_INT,
                gobject.TYPE_STRING, gobject.TYPE_STRING)

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

        def song_list(result):
            duration = 0
            last = None
            album = None
            songs = result.value()
            songs.sort(key=operator.itemgetter('album'))
            for song in songs:
                if last and last == song['album']:
                    album.increase_size()
                    album.add_duration(song['duration'])
                else:
                    if album:
                        self.add_album(album)
                    album = Album(self, self.__xmms, song['album'],
                            song['artist'], song['picture_front'], 1,
                            song['duration'])

                last = song['album']

            self.add_album(album)

        self.__xmms.coll_query_infos(xc.Universe(),
                ['id', 'album', 'artist', 'duration', 'picture_front'],
                cb=song_list)

        def id_list(result):
            self.__xmms.playlist_clear('_album')
            for id in result.value():
                self.__xmms.playlist_add_id(id, '_album')
            self.__xmms.playlist_load('_album')

        def selection_changed(selection, user_data):
           (model, rows) = selection.get_selected_rows()
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
           self.__xmms.coll_query_ids(coll, cb=id_list)

        self.get_selection().connect('changed', selection_changed, None)


    def __increase_ids(self):
        self.__ids = self.__ids + 1


    def add_album(self, album):
        """
        Adds an Album to the list
        """

        # FIXME: Escape album name, etc.
        self.list_store.append([None,
            '<b>%s</b>\n%s <small>- %d Tracks/%d:%02d Minutes</small>' %
            (album.name, album.artist, album.size, album.get_duration_min(),
                album.get_duration_sec()),
            self.__ids, album.artist, album.name])

        album.set_id(self.__ids)
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
