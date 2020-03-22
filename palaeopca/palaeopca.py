## Standard library
import os
import sys

## PPCA
import palaeopca
import palaeopca.P1Utils.P1PixmapCache

def main():
    from palaeopca import app

    # set icon and pixmap path
    defaultIconPaths = [
        os.path.join(palaeopca.basedir, "icons"),
    ]

    for defaultIconPath in defaultIconPaths:
        palaeopca.P1Utils.P1PixmapCache.addSearchPath(defaultIconPath)

    return app.run()