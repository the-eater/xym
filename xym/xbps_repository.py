from io import BytesIO
import tarfile
from xml.etree.ElementTree import XMLParser
import plistlib

import requests
from ratking.repository import MemoryRepository

from .xbps_plist_parser import XbpsPlistParser
from .xbps_rat import XbpsRat


class XbpsRepository(MemoryRepository):
    is_repo = True

    def __init__(self, url, is_repo=True):
        super().__init__(rats={}, name="An XBPS repository")

        self.is_repo = is_repo
        self.url = url

    def load(self):
        index = None

        if self.is_repo:
            result = requests.get(self.url)

            tar = tarfile.open(fileobj=BytesIO(result.content))
            index = tar.extractfile('index.plist')
        else:
            index = open(self.url, 'r')

        self.loaded = True

        self.load_plist(index)

    def save(self):
        if self.is_repo:
            raise RuntimeError("Can't save a remote repo")

        plist_dict = {}

        for name, rats in self.rats:
            if len(rats) == 0:
                continue

            rat_dict = self.rat_from_xbps(rats[0])

            if rat_dict is None:
                continue

            plist_dict[name] = rat_dict

        plistlib.dump(plist_dict, open(self.url, 'w+'))

    @staticmethod
    def rat_to_xbps_dict(rat):
        if not isinstance(rat, XbpsRat):
            return None

        return rat.raw_dict

    def load_plist(self, src):
        def rat_iter(dict, key):
            if key == '_XBPS_ALTERNATIVES_':
                return

            nonlocal self

            rat = self.rat_from_xbps(dict, repo=self)
            if rat:
                self.index(rat)

        parser = XMLParser(target=XbpsPlistParser(iterator=rat_iter))

        while True:
            data = src.read(16 * 1024)
            if not data:
                break

            parser.feed(data)

        parser.close()

    @staticmethod
    def rat_from_xbps(rat_dict, repo=None):
        parts = rat_dict['pkgver'].rsplit('-', maxsplit=1)

        name = parts[0]
        ver = parts[1]

        if name == 'cross-vpkg-dummy':
            return None

        rat = XbpsRat(name, raw_version=ver, raw_dict=rat_dict, repo=repo)

        return rat
