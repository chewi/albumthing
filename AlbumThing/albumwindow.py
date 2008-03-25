# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk
import menu, albumlist, playlist, controls, aboutdialog, preferencesdialog
import gobject
from albumthing import AlbumThing
import const


class AlbumWindow(gtk.Window):
    """
    The main window
    """

    def __init__(self):
        super(AlbumWindow, self).__init__(gtk.WINDOW_TOPLEVEL)

        self.__at = AlbumThing()

        self.__cb_foo = False

        self.set_title('Album')

        self.album_list = albumlist.AlbumListThing()
        self.playlist = playlist.PlayListThing()
        self.controls = controls.AlbumControls()
        self.vbox = gtk.VBox(homogeneous=False, spacing=8)
        self.about_dialog = aboutdialog.AboutDialog()
        self.preferences_dialog = preferencesdialog.PreferencesDialog(self)

        self.hpaned = gtk.HPaned()
        self.hpaned.set_position(
                int(self.__at.configuration.get('win', 'pos_hpaned')))

        self.hpaned.add1(self.album_list)
        self.hpaned.add2(self.playlist)

        self.menu_bar = menu.MenuBar()
        self.add_accel_group(self.menu_bar.accel_group)

        self.vbox.pack_start(self.menu_bar.item_factory.get_widget('<main>'),
                expand=False)
        self.vbox.pack_start(self.controls, expand=False)
        self.vbox.pack_start(self.hpaned)

        accel_group = gtk.AccelGroup()
        accel_group.connect_group(ord('L'), gtk.gdk.CONTROL_MASK,
                gtk.ACCEL_VISIBLE, self.focus_filter_entry)
        self.add_accel_group(accel_group)

        self.set_default_size(int(self.__at.configuration.get('win', 'width')),
                int(self.__at.configuration.get('win', 'height')))

        x = int(self.__at.configuration.get('win', 'pos_x'))
        y = int(self.__at.configuration.get('win', 'pos_y'))
        if x and y:
            self.move(x, y)

        try:
            gobject.timeout_add_seconds(1, self.__check_connection)
        except AttributeError:
            gobject.timeout_add(1000, self.__check_connection)

        self.add(self.vbox)
        self.connect('destroy', self.destroy)
        self.show_all()


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
                self.album_list.filter_entry.grab_focus()
        else:
            self.__cb_foo = False
            self.__widgets_set_sensitive(False)
            self.album_list.album_list.list_store.clear()
            self.album_list.filter_entry.set_text('')
            self.playlist.playlist.list_store.clear()
            self.controls.info_label.set_markup('<b>Not Connected</b>')
            self.controls.cover_art.clear()
            self.controls.seek_bar.scale.set_value(0)
            self.controls.seek_bar.time.set_text('-')

        return True


    def __widgets_set_sensitive(self, sens):
        self.album_list.set_sensitive(sens)
        self.playlist.set_sensitive(sens)
        self.controls.set_sensitive(sens)


    def focus_filter_entry(self, accel_group, acceleratable, keyval, modifier):
        self.album_list.filter_entry.grab_focus()


    def destroy(self, widget, data=None):
        self.__at.quit()


    def setup_callbacks(self):
        self.__at.xmms.playback_current_id(cb=self.__xmms_cb_current_id)
        self.__at.xmms.broadcast_playback_current_id(
                cb=self.__xmms_cb_current_id)

        self.album_list.setup_callbacks()
        self.playlist.setup_callbacks()
        self.controls.setup_callbacks()
