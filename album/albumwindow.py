# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk
import menu, albumlist, playlist, controls


class AlbumWindow(gtk.Window):
    """
    The main window
    """

    def __init__(self, xmms):
        super(AlbumWindow, self).__init__(gtk.WINDOW_TOPLEVEL)

        self.__xmms = xmms

        self.set_title('Album')

        self.album_list = albumlist.AlbumListThing(self.__xmms)
        self.play_list = playlist.PlayList(self.__xmms)
        self.vbox = gtk.VBox(homogeneous=False, spacing=8)

        self.hpaned = gtk.HPaned()

        scrolled_playlist = gtk.ScrolledWindow()
        scrolled_playlist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_playlist.set_shadow_type(gtk.SHADOW_IN)
        scrolled_playlist.add(self.play_list)

        self.hpaned.add1(self.album_list)
        self.hpaned.add2(scrolled_playlist)

        self.vbox.pack_start(menu.MenuBar(), expand=False)
        self.vbox.pack_start(controls.AlbumControls(self.__xmms), expand=False)
        self.vbox.pack_start(self.hpaned)

        self.__xmms.playback_current_id(cb=self.__xmms_cb_current_id)
        self.__xmms.broadcast_playback_current_id(cb=self.__xmms_cb_current_id)

        self.add(self.vbox)
        self.connect('destroy', self.destroy)
        self.show_all()


    def __xmms_cb_id_info(self, result):
        try:
            artist = result.value()['artist']
        except KeyError:
            artist = 'Unknown'
        try:
            title = result.value()['title']
        except KeyError:
            title = 'Unknown (%s)' % result.value()['url']
        self.set_title('%s - %s' % (artist, title))


    def __xmms_cb_current_id(self, result):
        self.__xmms.medialib_get_info(result.value(), cb=self.__xmms_cb_id_info)


    def destroy(self, widget, data=None):
        print 'bye'
        gtk.main_quit()
