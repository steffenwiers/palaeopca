import os

from PyQt5.QtWidgets import QStyle
from PyQt5.QtGui import QPixmap, QIcon


class P1PixmapCache(object):
    """
    Class implementing a pixmap cache for icons.
    """
    def __init__(self):
        """
        Constructor
        """
        self.pixmapCache = {}
        self.searchPath = []

    def getPixmap(self, key, style = ""):
        """
        Public method to retrieve a pixmap.

        :param key: name of the wanted pixmap (string)
        :return: the requested pixmap (QPixmap)
        """
        if key:
            try:
                return self.pixmapCache[key]
            except KeyError:
                if not os.path.isabs(key):
                    for path in self.searchPath:
                        pm = QPixmap(os.path.join(path, style, key + ".svg"))
                        if not pm.isNull():
                            break
                        else:
                            pm = QPixmap()
                else:
                    pm = QPixmap(key)
                self.pixmapCache[key] = pm
                return self.pixmapCache[key]
        return QPixmap()

    def addSearchPath(self, path):
        """
        Public method to add a path to the search path.

        :param path: path to add (string)
        """
        if path not in self.searchPath:
            self.searchPath.append(path)

pixCache = P1PixmapCache()


def getPixmap(key, cache=pixCache):
    """
    Module function to retrieve a pixmap.

    :param key: name of the wanted pixmap (string)
    :param cache: reference to the pixmap cache object (PixmapCache)
    :return: the requested pixmap (QPixmap)
    """
    return cache.getPixmap(key)


def getIcon(key, style = "", cache = pixCache):
    """
    Module function to retrieve an icon.

    :param key: name of the wanted icon (string)
    :param cache: reference to the pixmap cache object (PixmapCache)
    :return: the requested icon (QIcon)
    """
    return QIcon(cache.getPixmap(key, style))


def addSearchPath(path, cache = pixCache):
    """
    Module function to add a path to the search path.

    :param path: path to add (string)
    :param cache: reference to the pixmap cache object (PixmapCache)
    """
    cache.addSearchPath(path)
