# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from albumthing import AlbumThing


class MenuBar:
    def __init__(self, ui):
        self.__at = AlbumThing()

        menu_items = """
<ui>
  <menubar name="menubar">
    <menu action="file">
      <menuitem action="prefs" />
      <menuitem action="quit" />
    </menu>
    <menu action="control">
      <menuitem action="random" />
    </menu>
    <menu action="help">
      <menuitem action="about" />
    </menu>
  </menubar>
</ui>
"""

        self.uimanager = Gtk.UIManager()
        self.accel_group = self.uimanager.get_accel_group()
        action_group = Gtk.ActionGroup('AlbumThing')

        action_group.add_actions(
            [('file', None, '_File'),
             ('prefs', Gtk.STOCK_PREFERENCES, '_Preferences', None, None, self.preferences_resp),
             ('quit', Gtk.STOCK_QUIT, '_Quit', '<control>q', None, self.quit_resp),
             ('control', None, '_Control'),
             ('random', Gtk.STOCK_REFRESH, '_Random Album', '<control>m', None, self.rand_resp),
             ('help', None, '_Help'),
             ('about', Gtk.STOCK_ABOUT, '_About', None, None, self.info_resp)]
        )

        self.uimanager.insert_action_group(action_group, 0)
        self.uimanager.add_ui_from_string(menu_items)


    def info_resp(self, action = None):
        self.__at.win.about_dialog.run_and_hide(self.__at.win)


    def quit_resp(self, action = None):
        self.__at.quit()


    def preferences_resp(self, action = None):
        self.__at.win.preferences_dialog.run()


    def rand_resp(self, action = None):
        self.__at.win.album_list.album_list.random_album()
