## Standard library
import os
import sys

## PPCA
import ppca
import ppca.P1Utils.P1PixmapCache

def main():
    from ppca import app

    # set icon and pixmap path
    defaultIconPaths = [
        os.path.join(ppca.basedir, "icons", "fontawesome-free"),
    ]

    for defaultIconPath in defaultIconPaths:
        ppca.P1Utils.P1PixmapCache.addSearchPath(defaultIconPath)

    return app.run()