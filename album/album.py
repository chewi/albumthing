import pygtk
pygtk.require('2.0')
import gtk
import gobject


class Album:
    def __init__(self, albumlist, xmms, name, artist, picture_front, size=0,
            duration=0):
        self.__album_list = albumlist
        def __bindata_retrieve(result):
            try:
                self.__pixbuf_loader.write(result.value())
                self.__pixbuf_loader.close()
                if self.__id > -1:
                    albumlist.set_cover(self.__id,
                            self.__pixbuf_loader.get_pixbuf())
            except:
                pass

        self.__xmms = xmms
        self.__pixbuf_loader = gtk.gdk.PixbufLoader()
        self.__id = -1
        self.name = name
        self.artist = artist
        self.size = size
        self.duration = duration
        self.picture_front = picture_front

        if picture_front:
            xmms.bindata_retrieve(picture_front, cb=__bindata_retrieve)


    def increase_size(self, size=1):
        self.size = self.size + size


    def add_duration(self, duration):
        self.duration = self.duration + duration


    def get_cover_image(self):
        return self.__pixbuf_loader.get_pixbuf()


    def get_duration_min(self):
        return self.duration / 60000


    def get_duration_sec(self):
        return (self.duration / 1000) % 60


    def set_id(self, id):
        self.__id = id
        if self.__pixbuf_loader.get_pixbuf():
            albumlist.set_cover(self.__id, self.__pixbuf_loader.get_pixbuf())
