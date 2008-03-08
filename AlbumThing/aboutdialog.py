# Copyright (c) 2008 Sebastian Sareyko <smoon at nooms dot de>
# See COPYING file for details.


import pygtk
pygtk.require('2.0')
import gtk
import const


class AboutDialog(gtk.AboutDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()

        self.set_name(const.NAME)
        self.set_version(const.VERSION)
        self.set_copyright('Copyright \xc2\xa9 2008 Sebastian Sareyko')
        self.set_website(const.URL)
        self.set_comments(const.DESC)
        self.set_authors(['Sebastian Sareyko <smoon@nooms.de>'])
        self.set_license(
"Redistribution and use in source and binary forms, with or without\n"
"modification, are permitted provided that the following conditions are met:\n"
"\n"
"  * Redistributions of source code must retain the above copyright notice,\n"
"    this list of conditions and the following disclaimer.\n"
"\n"
"  * Redistributions in binary form must reproduce the above copyright notice,\n"
"    this list of conditions and the following disclaimer in the documentation\n"
"    and/or other materials provided with the distribution.\n"
"\n"
"  * Neither the name of the project nor the names of its contributors\n"
"    may be used to endorse or promote products derived from this software\n"
"    without specific prior written permission.\n"
"\n"
"THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS\n"
"\"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT\n"
"LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR\n"
"A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR\n"
"CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,\n"
"EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,\n"
"PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR\n"
"PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF\n"
"LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING\n"
"NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS\n"
"SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.")

        self.connect('response', self.__gtk_cb_response)


    def __gtk_cb_response(self, widget, resp):
        if resp == gtk.RESPONSE_CANCEL:
            self.hide()
