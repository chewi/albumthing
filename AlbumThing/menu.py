# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk
from albumthing import AlbumThing


class MenuBar:
    def __init__(self):
        self.__at = AlbumThing()

        self.menu_items = (
            (_('/_File'), None, None, 0, '<Branch>'),
            (_('/_File/_Preferences'), None, self.preferences_resp, 0, None),
            (_('/_File/sep'), None, None, 0, '<Separator>'),
            (_('/_File/_Quit'), '<control>Q', self.quit_resp, 0, None),
            (_('/_Control'), None, None, 0, '<Branch>'),
            (_('/_Control/Select _Random Album'), '<control>M',
                self.rand_resp, 0, None),
            (_('/_Help'), None, None, 0, '<Branch>'),
            (_('/_Help/_About'), None, self.info_resp, 0, None),
        )

        self.accel_group = gtk.AccelGroup()
        self.item_factory = gtk.ItemFactory(gtk.MenuBar, '<main>',
                self.accel_group)
        self.item_factory.create_items(self.menu_items)


    def info_resp(self, widget, string):
        self.__at.win.about_dialog.run()


    def quit_resp(self, widget, string):
        self.__at.quit()


    def preferences_resp(self, widget, string):
        self.__at.win.preferences_dialog.run()


    def rand_resp(self, widget, string):
        self.__at.win.album_list.album_list.random_album()
