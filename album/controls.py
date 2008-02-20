import pygtk
pygtk.require('2.0')
import gtk
import gobject
import xmmsclient


class AlbumControls(gtk.VBox):
    def __init__(self, xmms):
        super(AlbumControls, self).__init__(homogeneous=False, spacing=4)

        self.__xmms = xmms

        self.button_box = gtk.HBox(homogeneous=False, spacing=4)

        self.play_pause_button = gtk.ToggleButton(use_underline=False)
        self.play_pause_button.set_mode(False)
        self.play_pause_button.set_use_stock(True)
        self.play_pause_button.set_label(gtk.STOCK_MEDIA_PLAY)
        self.button_box.pack_start (self.play_pause_button, False, False)

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

        self.pack_start(self.button_box, expand=False)

        self.play_pause_button.connect('toggled',
                self.__gtk_cb_play_pause_toggled, None)
        self.prev_button.connect('clicked', self.__gtk_cb_prev_clicked, None)
        self.next_button.connect('clicked', self.__gtk_cb_next_clicked, None)

        self.__xmms.playback_status(cb=self.__xmms_cb_playback_status)
        self.__xmms.broadcast_playback_status(cb=self.__xmms_cb_playback_status)


    def __xmms_cb_playback_status(self, result):
        status = result.value()
        if status == xmmsclient.PLAYBACK_STATUS_PAUSE or \
                status == xmmsclient.PLAYBACK_STATUS_STOP:
            self.play_pause_button.set_active(False)
        elif status == xmmsclient.PLAYBACK_STATUS_PLAY:
            self.play_pause_button.set_active(True)


    def __gtk_cb_play_pause_toggled(self, button, user_data):
        if self.play_pause_button.get_active():
            self.__xmms.playback_start()
        else:
            self.__xmms.playback_pause()


    def __gtk_cb_prev_clicked(self, button, user_data):
        self.__xmms.playlist_set_next_rel(-1)
        self.__xmms.playback_tickle()


    def __gtk_cb_next_clicked(self, button, user_data):
        self.__xmms.playlist_set_next_rel(1)
        self.__xmms.playback_tickle()
