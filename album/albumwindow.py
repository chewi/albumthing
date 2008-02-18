import pygtk
pygtk.require('2.0')
import gtk
import menu, albumlist


class AlbumWindow(gtk.Window):
    """
    The main window
    """

    def __init__(self, xmms):
        super(AlbumWindow, self).__init__(gtk.WINDOW_TOPLEVEL)

        self.xmms = xmms

        self.album_list = albumlist.AlbumList(self.xmms)
        self.vbox = gtk.VBox(homogeneous=False, spacing=4)

        self.hpaned = gtk.HPaned()

        scrolled_album = gtk.ScrolledWindow()
        scrolled_album.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_album.add(self.album_list)

        self.hpaned.add1(scrolled_album)

        self.vbox.pack_start(menu.MenuBar(), expand=False)
        # FIXME: Add Controls, etc. here
        self.vbox.pack_start(self.hpaned)

        self.add(self.vbox)
        self.connect('destroy', self.destroy)
        self.show_all()


    def destroy(self, widget, data=None):
        print 'bye'
        gtk.main_quit()
