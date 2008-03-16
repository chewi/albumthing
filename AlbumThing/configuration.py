# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import ConfigParser
import os
import xmmsclient
from albumthing import AlbumThing


class Configuration:
    def __init__(self):
        self.__at = AlbumThing ()

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
            self.__cfg.set('ui', 'combine_va_albums', '0')
            self.__cfg.add_section('win')
            self.__cfg.set('win', 'width', '500')
            self.__cfg.set('win', 'height', '600')
            self.__cfg.set('win', 'pos_x', '0')
            self.__cfg.set('win', 'pos_y', '0')
            self.__cfg.set('win', 'pos_hpaned', '160')


    def get(self, section, var):
        try:
            ret = self.__cfg.get (section, var)
            if ret == '0':
                ret = 0
        except:
            ret = None

        return ret


    def set(self, section, var, value):
        self.__cfg.set(section, var, value)


    def save(self):
        try:
            self.__cfg.add_section('win')
        except ConfigParser.DuplicateSectionError:
            pass
        self.__cfg.set('win', 'width', self.__at.win.get_size()[0])
        self.__cfg.set('win', 'height', self.__at.win.get_size()[1])
        self.__cfg.set('win', 'pos_x', self.__at.win.get_position()[0])
        self.__cfg.set('win', 'pos_y', self.__at.win.get_position()[1])
        self.__cfg.set('win', 'pos_hpaned', self.__at.win.hpaned.get_position())
        try:
            fd = open (self.__configuration_file, 'w')
            self.__cfg.write(fd)
        except IOError:
            pass
