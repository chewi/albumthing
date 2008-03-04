# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import ConfigParser
import os
import xmmsclient

class Configuration:
    def __init__(self):
        self.__cfg = ConfigParser.ConfigParser()
        self.__configuration_file = os.path.join(xmmsclient.userconfdir_get(),
                'clients', 'AlbumThing.ini')
        try:
            fd = open (self.__configuration_file, 'r')
            self.__cfg.readfp(fd)
        except IOError:
            self.__cfg.add_section('common')
            self.__cfg.set('common', 'start_xmms2d', '0')
            self.__cfg.add_section('ui')
            self.__cfg.set('ui', 'show_cover_art', '1')
            self.__cfg.set('ui', 'show_alternative_cover_art', '0')


    def get(self, section, var):
        try:
            ret = self.__cfg.get (section, var)
            if ret == '1':
                ret = True
            elif ret == '0':
                ret = False
        except:
            ret = None

        return ret


    def set(self, section, var, value):
        self.__cfg.set(section, var, value)


    def save(self):
        try:
            fd = open (self.__configuration_file, 'w')
            self.__cfg.write(fd)
        except IOError:
            pass
