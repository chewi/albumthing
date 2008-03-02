# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk

class PreferencesDialog(gtk.Dialog):
    def __init__(self, parent):
        super(PreferencesDialog, self).__init__(title='Preferences',
                parent=parent, flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.__start_xmms2d_check_button = gtk.CheckButton(
                'Automatically start xmms2d')
        self.__start_xmms2d_check_button.show()
        self.vbox.pack_start(self.__start_xmms2d_check_button,
                True, True, 0)

        self.__cover_art_check_button = gtk.CheckButton(
                'Show Cover Art in the album list')
        self.__cover_art_check_button.show()
        self.vbox.pack_start(self.__cover_art_check_button,
                True, True, 0)

        alignment = gtk.Alignment()
        alignment.set_padding(0, 0, 20, 0)
        self.__alternative_cover_art_check_button = gtk.CheckButton(
                'Show icons for albums without cover art')
        alignment.add(self.__alternative_cover_art_check_button)
        alignment.show_all()
        self.vbox.pack_start(alignment, True, True, 0)

        self.connect('response', self.__gtk_cb_response)
        self.__start_xmms2d_check_button.connect('toggled',
                self.__gtk_cb_start_xmms2d_toggled)
        self.__cover_art_check_button.connect('toggled',
                self.__gtk_cb_cover_art_toggled)
        self.__alternative_cover_art_check_button.connect('toggled',
                self.__gtk_cb_alternative_cover_art_toggled)


    def __gtk_cb_response(self, widget, resp):
        if resp == gtk.RESPONSE_CLOSE:
            self.hide()


    def __gtk_cb_start_xmms2d_toggled(self, togglebutton):
        pass


    def __gtk_cb_cover_art_toggled(self, togglebutton):
        if self.__cover_art_check_button.get_active():
            self.__alternative_cover_art_check_button.set_sensitive(True)
        else:
            self.__alternative_cover_art_check_button.set_sensitive(False)


    def __gtk_cb_alternative_cover_art_toggled(self, togglebutton):
        pass
