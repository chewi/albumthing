# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.



import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
import xmmsclient
from .albumthing import AlbumThing
from .coverart import CoverArt
from . import const


class SeekBar(Gtk.VBox):
    def __init__(self):
        super(SeekBar, self).__init__(homogeneous=False, spacing=4)

        self.__at = AlbumThing()
        self.__duration = 0

        self.scale = Gtk.HScale()
        self.scale.set_draw_value(False)
        self.scale.set_range(0, 1)
        self.pack_start(self.scale, True, True, 0)

        self.time = Gtk.Label(label='-')
        self.pack_start(self.time, True, True, 0)

        self.scale.connect('change-value', self.__gtk_cb_change_value, None)

        try:
            GObject.timeout_add_seconds(1, self.__poll_playtime)
        except AttributeError:
            GObject.timeout_add(1000, self.__poll_playtime)


    def __xmms_cb_id_info(self, result):
        if not result.value():
            return
        try:
            self.__duration = result.value()['duration']
        except KeyError:
            # FIXME: Non-seekable stream?
            pass


    def __xmms_cb_current_id(self, result):
        self.__at.xmms.medialib_get_info(result.value(),
                cb=self.__xmms_cb_id_info)


    def __xmms_cb_playback_playtime(self, result):
        if self.__duration < 1:
            self.scale.set_sensitive(False)
            self.time.set_text('-')
        else:
            self.scale.set_sensitive(True)
            self.scale.set_value(result.value() / self.__duration)
            self.time.set_text('%s / %s' % 
                    (self.__format_time(result.value()),
                        self.__format_time(self.__duration)))


    def __poll_playtime(self):
        if self.__at.connected:
            self.__at.xmms.playback_playtime(
                    cb=self.__xmms_cb_playback_playtime)
        return True


    def __gtk_cb_change_value(self, range, scroll, value, user_data):
        time = value * self.__duration
        self.__at.xmms.playback_seek_ms(time)


    def __format_time(self, time):
        return '%d:%02d' % (int(time / 60000), int((time / 1000) % 60))


    def setup_callbacks(self):
        self.__at.xmms.playback_current_id(cb=self.__xmms_cb_current_id)
        self.__at.xmms.broadcast_playback_current_id(
                cb=self.__xmms_cb_current_id)


class AlbumControls(Gtk.VBox):
    def __init__(self):
        super(AlbumControls, self).__init__(homogeneous=False, spacing=4)

        self.__at = AlbumThing()

        self.button_box = Gtk.HBox(homogeneous=False, spacing=4)

        self.play_pause_button = Gtk.ToggleButton()
        self.play_pause_button.set_mode(False)
        self.play_pause_button.set_use_stock(True)
        self.play_pause_button.set_label(Gtk.STOCK_MEDIA_PLAY)
        self.button_box.pack_start (self.play_pause_button, False, False, 4)

        self.prev_button = Gtk.Button(stock=Gtk.STOCK_MEDIA_PREVIOUS)
        label = self.prev_button.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label.set_text('')
        self.button_box.pack_start (self.prev_button, False, False, 0)

        self.next_button = Gtk.Button(stock=Gtk.STOCK_MEDIA_NEXT)
        label = self.next_button.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label.set_text('')
        self.button_box.pack_start (self.next_button, False, False, 0)

        self.seek_bar = SeekBar()
        self.button_box.pack_start(self.seek_bar, True, True, 4)

        self.pack_start(self.button_box, False, True, 0)

        self.cover_art = Gtk.Image()

        self.info_label = Gtk.Label(label='<b>Not Connected</b>')
        self.info_label.set_use_markup(True)
        self.info_label.set_selectable(True)

        label_holder = Gtk.HBox(homogeneous=False)
        label_holder.pack_start(self.cover_art, False, False, 4)
        label_holder.pack_start(self.info_label, False, False, 4)

        self.pack_start(label_holder, True, True, 0)

        self.play_pause_button.connect('toggled',
                self.__gtk_cb_play_pause_toggled, None)
        self.prev_button.connect('clicked', self.__gtk_cb_prev_clicked, None)
        self.next_button.connect('clicked', self.__gtk_cb_next_clicked, None)

        if self.__at.connected:
            self.setup_callbacks()


    def __xmms_cb_playback_status(self, result):
        status = result.value()
        if status == xmmsclient.PLAYBACK_STATUS_PAUSE or \
                status == xmmsclient.PLAYBACK_STATUS_STOP:
            self.play_pause_button.set_active(False)
        elif status == xmmsclient.PLAYBACK_STATUS_PLAY:
            self.play_pause_button.set_active(True)


    def __xmms_cb_id_info(self, result):
        if not result.value():
            # Wtf? Why is xmms2 not giving us the information we requested?
            self.info_label.set_markup(_('<b>No info found</b>\nI blame xmms2'))
            return

        try:
            picture_front = result.value()['picture_front']
            self.__at.xmms.bindata_retrieve(picture_front,
                    cb=self.__xmms_cb_bindata_retrieve)
        except KeyError:
            ca = CoverArt(None, 64)
            self.cover_art.set_from_pixbuf(ca.pixbuf)

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

        self.info_label.set_markup(
                '<b>%s</b>\n<small>by</small> %s <small>from</small> %s' %
                (GLib.markup_escape_text(title), GLib.markup_escape_text(artist),
                    GLib.markup_escape_text(album)))


    def __xmms_cb_bindata_retrieve(self, result):
        ca = CoverArt(result.value(), 64)
        self.cover_art.set_from_pixbuf(ca.pixbuf)


    def __xmms_cb_current_id(self, result):
        self.__at.xmms.medialib_get_info(result.value(),
                cb=self.__xmms_cb_id_info)


    def __gtk_cb_play_pause_toggled(self, button, user_data):
        if self.play_pause_button.get_active():
            self.__at.xmms.playback_start()
        else:
            self.__at.xmms.playback_pause()


    def __gtk_cb_prev_clicked(self, button, user_data):
        self.__at.xmms.playlist_set_next_rel(-1)
        self.__at.xmms.playback_tickle()


    def __gtk_cb_next_clicked(self, button, user_data):
        self.__at.xmms.playlist_set_next_rel(1)
        self.__at.xmms.playback_tickle()


    def setup_callbacks(self):
        self.__at.xmms.playback_status(cb=self.__xmms_cb_playback_status)
        self.__at.xmms.broadcast_playback_status(
                cb=self.__xmms_cb_playback_status)
        self.__at.xmms.playback_current_id(cb=self.__xmms_cb_current_id)
        self.__at.xmms.broadcast_playback_current_id(
                cb=self.__xmms_cb_current_id)
        self.seek_bar.setup_callbacks()
