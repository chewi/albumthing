# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk
import menu, albumlist, playlist, controls
import gobject
from albumthing import AlbumThing


class AlbumWindow(gtk.Window):
    """
    The main window
    """

    def __init__(self):
        super(AlbumWindow, self).__init__(gtk.WINDOW_TOPLEVEL)

        self.__at = AlbumThing ()

        self.__cb_foo = False

        self.set_title('Album')

        self.album_list = albumlist.AlbumListThing()
        self.playlist = playlist.PlayList()
        self.controls = controls.AlbumControls()
        self.vbox = gtk.VBox(homogeneous=False, spacing=8)

        self.hpaned = gtk.HPaned()

        scrolled_playlist = gtk.ScrolledWindow()
        scrolled_playlist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_playlist.set_shadow_type(gtk.SHADOW_IN)
        scrolled_playlist.add(self.playlist)

        self.hpaned.add1(self.album_list)
        self.hpaned.add2(scrolled_playlist)

        self.vbox.pack_start(menu.MenuBar(), expand=False)
        self.vbox.pack_start(self.controls, expand=False)
        self.vbox.pack_start(self.hpaned)

        if self.__at.connected:
            self.setup_callbacks()
        else:
            self.__widgets_set_sensitive(False)

        self.album_list.filter_grab_focus()

        gobject.timeout_add_seconds(1, self.__check_connection)

        self.add(self.vbox)
        self.connect('destroy', self.destroy)
        self.show_all()


    def __xmms_cb_id_info(self, result):
        if not result.value():
            return

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
        self.__at.xmms.medialib_get_info(result.value(),
                cb=self.__xmms_cb_id_info)


    def __check_connection(self):
        if self.__at.connected:
            if not self.__cb_foo:
                self.__cb_foo = True
                self.setup_callbacks()
                self.__widgets_set_sensitive(True)
        else:
            self.__cb_foo = False
            self.__widgets_set_sensitive(False)
            self.album_list.album_list.list_store.clear()
            self.album_list.filter_entry.set_text('')
            self.playlist.list_store.clear()

        return True


    def __widgets_set_sensitive(self, sens):
        self.album_list.set_sensitive(sens)
        self.playlist.set_sensitive(sens)
        self.controls.set_sensitive(sens)


    def destroy(self, widget, data=None):
        print 'bye'
        gtk.main_quit()


    def setup_callbacks(self):
        self.__at.xmms.playback_current_id(cb=self.__xmms_cb_current_id)
        self.__at.xmms.broadcast_playback_current_id(
                cb=self.__xmms_cb_current_id)

        self.album_list.setup_callbacks()
        self.playlist.setup_callbacks()
        self.controls.setup_callbacks()
