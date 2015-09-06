# e621 Downloader
# Copyright (C) 2014, "Glitch"
# http://www.glitchfur.net/

from distutils.core import setup
import py2exe

import version

setup(
    name = version.NAME,
    description = version.DESCRIPTION,
    version = version.VERSION,
    license = version.LICENSE,
    author = version.AUTHOR,
    author_email = version.EMAIL,
    url = version.URL,
    
    data_files = [("",["icon.ico",
                        "doc/CHANGELOG.TXT",
                        "doc/LICENSE.txt",
                        "doc/README.txt",
                        "doc/TODO.txt"])],
    
    windows = [
       {
            "script": "e621dl.py",
            "icon_resources": [(0, "icon.ico")]
       }
    ]
    )
