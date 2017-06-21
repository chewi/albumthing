# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from albumthing import AlbumThing


class PreferencesDialog(Gtk.Dialog):
    def __init__(self, parent):
        super(PreferencesDialog, self).__init__(title='Preferences',
                parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
                buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))

        self.__at = AlbumThing()
        self.__parent = parent

        self.__notebook = Gtk.Notebook()
        self.__notebook.set_tab_pos(Gtk.PositionType.TOP)
        self.vbox.pack_start(self.__notebook, True, True, 0)

        vbox = Gtk.VBox()

        self.__cover_art_check_button = Gtk.CheckButton(
                _('Show Cover Art in the album list'))
        self.__cover_art_check_button.show()
        vbox.pack_start(self.__cover_art_check_button,
                True, True, 0)

        alignment = Gtk.Alignment.new(0, 0, 0, 0)
        alignment.set_padding(0, 0, 20, 0)
        self.__alternative_cover_art_check_button = Gtk.CheckButton(
                _('Show icons for albums without cover art'))
        alignment.add(self.__alternative_cover_art_check_button)
        alignment.show_all()
        vbox.pack_start(alignment, True, True, 0)

        self.__combine_va_check_button = Gtk.CheckButton(
                _('Combine albums with various artists'))
        self.__combine_va_check_button.show()
        vbox.pack_start(self.__combine_va_check_button,
                True, True, 0)

        self.__notebook.append_page(vbox, Gtk.Label(label=_('User Interface')))

        vbox = Gtk.VBox()

        self.__start_xmms2d_check_button = Gtk.CheckButton(
                _('Automatically start xmms2d'))
        self.__start_xmms2d_check_button.show()
        vbox.pack_start(self.__start_xmms2d_check_button,
                True, True, 0)

        self.__random_album_check_button = Gtk.CheckButton(
                _('Play random album on stop'))
        self.__random_album_check_button.show()
        vbox.pack_start(self.__random_album_check_button,
                True, True, 0)

        self.__notebook.append_page(vbox, Gtk.Label(label=_('Behaviour')))
        self.__notebook.show_all()

        if self.__at.configuration.get('common', 'start_xmms2d'):
            self.__start_xmms2d_check_button.set_active(True)
        else:
            self.__start_xmms2d_check_button.set_active(False)

        if self.__at.configuration.get('behaviour', 'random_album'):
            self.__random_album_check_button.set_active(True)
        else:
            self.__random_album_check_button.set_active(False)

        if self.__at.configuration.get('ui', 'show_cover_art'):
            self.__cover_art_check_button.set_active(True)
        else:
            self.__cover_art_check_button.set_active(False)

        if self.__at.configuration.get('ui', 'show_alternative_cover_art'):
            self.__alternative_cover_art_check_button.set_active(True)
        else:
            self.__alternative_cover_art_check_button.set_active(False)

        if self.__at.configuration.get('ui', 'combine_va_albums'):
            self.__combine_va_check_button.set_active(True)
        else:
            self.__combine_va_check_button.set_active(False)

        self.connect('response', self.__gtk_cb_response)
        self.__start_xmms2d_check_button.connect('toggled',
                self.__gtk_cb_start_xmms2d_toggled)
        self.__random_album_check_button.connect('toggled',
                self.__gtk_cb_random_album_toggled)
        self.__cover_art_check_button.connect('toggled',
                self.__gtk_cb_cover_art_toggled)
        self.__alternative_cover_art_check_button.connect('toggled',
                self.__gtk_cb_alternative_cover_art_toggled)
        self.__combine_va_check_button.connect('toggled',
                self.__gtk_cb_combine_va_toggled)


    def __gtk_cb_response(self, widget, resp):
        if resp == Gtk.ResponseType.CLOSE:
            self.hide()


    def __gtk_cb_start_xmms2d_toggled(self, togglebutton):
        if self.__start_xmms2d_check_button.get_active():
            self.__at.configuration.set('common', 'start_xmms2d', '1')
        else:
            self.__at.configuration.set('common', 'start_xmms2d', '0')


    def __gtk_cb_random_album_toggled(self, togglebutton):
        if self.__random_album_check_button.get_active():
            self.__at.configuration.set('behaviour', 'random_album', '1')
        else:
            self.__at.configuration.set('behaviour', 'random_album', '0')


    def __gtk_cb_cover_art_toggled(self, togglebutton):
        if self.__cover_art_check_button.get_active():
            self.__alternative_cover_art_check_button.set_sensitive(True)
            self.__at.configuration.set('ui', 'show_cover_art', '1')
        else:
            self.__alternative_cover_art_check_button.set_sensitive(False)
            self.__at.configuration.set('ui', 'show_cover_art', '0')

        self.__parent.album_list.refresh()


    def __gtk_cb_alternative_cover_art_toggled(self, togglebutton):
        if self.__alternative_cover_art_check_button.get_active():
            self.__at.configuration.set('ui', 'show_alternative_cover_art', '1')
        else:
            self.__at.configuration.set('ui', 'show_alternative_cover_art', '0')

        self.__parent.album_list.refresh()


    def __gtk_cb_combine_va_toggled(self, togglebutton):
        if self.__combine_va_check_button.get_active():
            self.__at.configuration.set('ui', 'combine_va_albums', '1')
        else:
            self.__at.configuration.set('ui', 'combine_va_albums', '0')

        self.__parent.album_list.refresh()
