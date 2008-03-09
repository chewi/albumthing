# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk
from albumthing import AlbumThing


class MenuBar(gtk.MenuBar):
    def __init__(self):
        super(MenuBar, self).__init__()

        self.__at = AlbumThing ()

        menu = gtk.Menu()

        item = gtk.MenuItem(_('Preferences'))
        item.connect('activate', self.preferences_resp, None)
        menu.append(item)

        item = gtk.MenuItem(_('Quit'))
        item.connect('activate', self.quit_resp, None)
        menu.append(item)

        file_menu = gtk.MenuItem(_('File'))
        file_menu.set_submenu(menu)

        menu = gtk.Menu()

        item = gtk.MenuItem(_('Info'))
        item.connect('activate', self.info_resp, None)
        menu.append(item)

        help_menu = gtk.MenuItem(_('Help'))
        help_menu.set_submenu(menu)

        self.append(file_menu)
        self.append(help_menu)


    def info_resp(self, widget, string):
        self.__at.win.about_dialog.run()


    def quit_resp(self, widget, string):
        self.__at.quit()


    def preferences_resp(self, widget, string):
        self.__at.win.preferences_dialog.run()
