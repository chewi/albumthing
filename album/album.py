import pygtk
pygtk.require('2.0')
import gtk
import gobject


class Album:
    def __init__(self, xmms, name, artist, picture_front, size=0, duration=0):
        def __bindata_retrieve(result):
            buf = result.get_bin()
#            filename = self.picture_front
#            file = open(filename, 'w')
#            file.write(buf)
#            file.close
            self.__pixbuf_loader.write(buf)
            self.__pixbuf_loader.close()

        self.__xmms = xmms
        self.__pixbuf_loader = gtk.gdk.PixbufLoader()
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
