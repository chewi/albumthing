import pygtk
pygtk.require('2.0')
import gtk
import gobject
from xmmsclient import collections as xc
import operator
from album import Album


COVER_SIZE = 64


class AlbumList(gtk.TreeView):
    def __init__(self, xmms):
        super(AlbumList, self).__init__()

        self.xmms = xmms
        self.ids = 0

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
                    album = Album(self, xmms, song['album'], song['artist'],
                            song['picture_front'], 1, song['duration'])

                last = song['album']

            self.add_album(album)

        xmms.coll_query_infos(xc.Universe(),
                ['id', 'album', 'artist', 'duration', 'picture_front'],
                cb=song_list)


    def __increase_ids(self):
        self.ids = self.ids + 1


    def add_album(self, album):
        """
        Adds an Album to the list
        """

        # FIXME: Escape album name, etc.
        self.list_store.append([None, '<b>%s</b>\n%s <small>- %d Tracks/%d:%02d Minutes</small>' % (album.name, album.artist, album.size, album.get_duration_min(), album.get_duration_sec()), self.ids])

        album.set_id(self.ids)
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
