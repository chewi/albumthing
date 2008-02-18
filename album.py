#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import xmmsclient
from xmmsclient import collections as xc
from xmmsclient import glib as xmmsglib
import sys
import os
import operator
from album import albumwindow
from album.album import Album


if __name__ == '__main__':
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
#                album['songs'] = album['songs'] + 1
#                album['duration'] = album['duration'] + song['duration']
            else:
                if album:
                    win.album_list.add_album(album)
                album = Album(xmms, song['album'], song['artist'],
                        song['picture_front'], 1, song['duration'])
#                album = {'name': song['album'],
#                        'artist': song['artist'],
#                        'songs': 1,
#                        'duration': song['duration'],
#                        'picture_front': song['picture_front']}

            last = song['album']

        win.album_list.add_album(album)
#        win.album_list.add_album(album['name'], album['artist'], album['songs'], album['duration'], album['picture_front'], xmms)


    xmms = xmmsclient.XMMS('album')
    try:
        xmms.connect(os.getenv('XMMS_PATH'))
    except IOError, detail:
        print 'Connection failed: %s' % detail
        sys.exit(1)

    conn = xmmsglib.GLibConnector(xmms)

    xmms.coll_query_infos(xc.Universe(), ['id', 'album', 'artist', 'duration', 'picture_front'], cb=song_list)

    win = albumwindow.AlbumWindow(xmms)
    gtk.main()
