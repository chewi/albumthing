# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import os
import xmmsclient
from xmmsclient import glib as xmmsglib
import gobject


class AlbumThing(object):
    __instance = None


    class Singleton:
        def __init__(self):
            self.connected = False
            self.xmms = xmmsclient.XMMS('AlbumThing')
            self.__connect()
            gobject.timeout_add_seconds(1, self.__check_connection)


        def __xmms_cb_disconnect(self, user_data):
            self.connected = False


        def __connect(self):
            try:
                self.xmms.connect(os.getenv('XMMS_PATH'),
                        self.__xmms_cb_disconnect)
                self.conn = xmmsglib.GLibConnector(self.xmms)
                self.connected = True
            except IOError:
                self.connected = False


        def __check_connection(self):
            if not self.connected:
                self.__connect()
            return True


    def __init__(self):
        if AlbumThing.__instance is None:
            AlbumThing.__instance = AlbumThing.Singleton()


    def __getattr__(self, attr):
        return getattr(self.__instance, attr)


    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
