# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


from __future__ import division
import pygtk
pygtk.require('2.0')
import gtk
import gobject
from gobject import markup_escape_text
import xmmsclient
from albumthing import AlbumThing
from coverart import CoverArt
import const


class SeekBar(gtk.VBox):
    def __init__(self):
        super(SeekBar, self).__init__(homogeneous=False, spacing=4)

        self.__at = AlbumThing()
        self.__duration = 0

        self.scale = gtk.HScale()
        self.scale.set_draw_value(False)
        self.scale.set_range(0, 1)
        self.pack_start(self.scale)

        self.time = gtk.Label('-')
        self.pack_start(self.time)

        self.scale.connect('change-value', self.__gtk_cb_change_value, None)

        try:
            gobject.timeout_add_seconds(1, self.__poll_playtime)
        except AttributeError:
            gobject.timeout_add(1000, self.__poll_playtime)


    def __xmms_cb_id_info(self, result):
        if not result.value():
            return
        self.__duration = result.value()['duration']


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


class AlbumControls(gtk.VBox):
    def __init__(self):
        super(AlbumControls, self).__init__(homogeneous=False, spacing=4)

        self.__at = AlbumThing()

        self.button_box = gtk.HBox(homogeneous=False, spacing=4)

        self.play_pause_button = gtk.ToggleButton(use_underline=False)
        self.play_pause_button.set_mode(False)
        self.play_pause_button.set_use_stock(True)
        self.play_pause_button.set_label(gtk.STOCK_MEDIA_PLAY)
        self.button_box.pack_start (self.play_pause_button, False, False, 4)

        self.prev_button = gtk.Button(stock=gtk.STOCK_MEDIA_PREVIOUS)
        label = self.prev_button.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label.set_text('')
        self.button_box.pack_start (self.prev_button, False, False)

        self.next_button = gtk.Button(stock=gtk.STOCK_MEDIA_NEXT)
        label = self.next_button.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label.set_text('')
        self.button_box.pack_start (self.next_button, False, False)

        self.seek_bar = SeekBar()
        self.button_box.pack_start(self.seek_bar, padding=4)

        self.pack_start(self.button_box, expand=False)

        self.cover_art = gtk.Image()

        self.info_label = gtk.Label('<b>Not Connected</b>')
        self.info_label.set_use_markup(True)
        self.info_label.set_selectable(True)

        label_holder = gtk.HBox(homogeneous=False)
        label_holder.pack_start(self.cover_art, False, False, 4)
        label_holder.pack_start(self.info_label, False, False, 4)

        self.pack_start(label_holder)

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
                (markup_escape_text(title), markup_escape_text(artist),
                    markup_escape_text(album)))


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
