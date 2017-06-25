# Copyright (c) 2017 James Le Cuirot <chewi at gentoo dot org>
# See COPYING file for details.


from multiprocessing import Pool, Value
import ctypes
import os
import xmmsclient


class CoverArtFetcherProcess():
    enabled = None
    xmms = None

    @classmethod
    def init(klass, enabled, xmms):
        klass.enabled = enabled
        klass.xmms = xmms


    @classmethod
    def fetch(klass, id):
        if klass.enabled.value:
            result = klass.xmms.bindata_retrieve(id)
            result.wait()
            return result.value()


    @classmethod
    def ping(klass):
        pass


class CoverArtFetcher():
    def __init__(self):
        self.pool = None
        self.enabled = Value(ctypes.c_bool, True)
        self.xmms = xmmsclient.XMMS('AlbumThingCoverArtFetcher')
        self.connect()
        self.pool = Pool(processes=1, initializer=CoverArtFetcherProcess.init, initargs=[self.enabled, self.xmms])


    def reset(self):
        if self.pool:
            self.enabled.value = False
            self.pool.apply(CoverArtFetcherProcess.ping)
            self.enabled.value = True


    def connect(self):
        path = os.getenv('XMMS_PATH')

        try:
            self.xmms.connect(path)
        except OSError:
            pass


    def fetch_async(self, id, callback):
        self.pool.apply_async(CoverArtFetcherProcess.fetch, [id], callback=callback)
