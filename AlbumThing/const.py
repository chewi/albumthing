# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


try:
    gettext
except:
    import gettext
    gettext.install('albumthing')


NAME = 'AlbumThing'
VERSION = '0.1'
URL = 'http://nooms.de/'
DESC = _('A simple XMMS2 client')

UNKNOWN = _('Unknown')
COVER_SIZE = 40
