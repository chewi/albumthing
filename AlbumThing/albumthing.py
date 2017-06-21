# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk

import os
import xmmsclient
from xmmsclient import glib as xmmsglib
import gettext


class AlbumThing(object):
    __instance = None


    class Singleton:
        def __init__(self):
            self.connected = False
            self.xmms = xmmsclient.XMMS('AlbumThing')
            self.configuration = None
            self.win = None

            self.__connect()

            try:
                GObject.timeout_add_seconds(1, self.__check_connection)
            except AttributeError:
                GObject.timeout_add(1000, self.__check_connection)


        def __xmms_cb_disconnect(self, user_data):
            self.connected = False


        def __connect(self):
            try:
                self.xmms.connect(os.getenv('XMMS_PATH'),
                        self.__xmms_cb_disconnect)
                self.conn = xmmsglib.GiGLibConnector(self.xmms)
                self.connected = True
            except IOError:
                self.connected = False
                if self.configuration and \
                        self.configuration.get('common', 'start_xmms2d'):
                    os.system('xmms2-launcher')


        def __check_connection(self):
            if not self.connected:
                self.__connect()
            return True


        def quit(self):
            self.configuration.save()
            Gtk.main_quit()


    def __init__(self):
        if AlbumThing.__instance is None:
            from albumwindow import AlbumWindow
            from configuration import Configuration

            gettext.install('albumthing', unicode=True)

            AlbumThing.__instance = AlbumThing.Singleton()
            AlbumThing.__instance.configuration = Configuration()
            AlbumThing.__instance.win = AlbumWindow()

            Gtk.main()


    def __getattr__(self, attr):
        return getattr(self.__instance, attr)


    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
