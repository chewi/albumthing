import pygtk
pygtk.require('2.0')
import gtk

class MenuBar(gtk.MenuBar):
    def __init__(self):
        super(MenuBar, self).__init__()

        menu = gtk.Menu()

        item = gtk.MenuItem('Quit')
        item.connect('activate', self.quit_resp, None)
        menu.append(item)

        file_menu = gtk.MenuItem('File')
        file_menu.set_submenu(menu)

        menu = gtk.Menu()

        item = gtk.MenuItem('Info')
        item.connect('activate', self.info_resp, None)
        menu.append(item)

        help_menu = gtk.MenuItem('Help')
        help_menu.set_submenu(menu)

        self.append(file_menu)
        self.append(help_menu)


    def info_resp(self, widget, string):
        print 'This be an Info Dialog'


    def quit_resp(self, widget, string):
        gtk.main_quit()
