##############################################################################
##
## e621 Downloader
## Copyright (C) 2014, "Glitch"
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

from urllib import quote, urlopen
from xml.etree import ElementTree as ET

SITEADDRESS = "https://e621.net"
FILTERS = "?limit=100&page=%d"

class Query:
    def __init__(self, query, limit=None):
        self.query = query
        self.request = SITEADDRESS + "/post/index.xml" + FILTERS + "&tags=" + quote(self.query)
        self.posts = getpostcount(self.query)
        if limit and (limit < self.posts):
            self.posts = limit
        self.pages = (self.posts / 100) + 1 # 100-post pages
        self.type = 'query'
    def iter(self):
        """A generator that yields page objects."""
        for pagenum in xrange(1, (self.pages + 1)):
            response = urlopen(self.request % pagenum)
            page = ET.parse(response)
            yield page

class Pool(Query):
    def __init__(self, pool):
        self.pool = pool # this is an ID
        self.request = SITEADDRESS + "/pool/show.xml?page=%d&id=" + str(self.pool)
        # a nasty, temporary version of getpostcount() for pools
        tempdata = ET.fromstring(urlopen(self.request % 1).read())
        self.posts = int(tempdata.get('post_count'))
        self.pages = (self.posts / 24) + 1 # apparently pools are limited to 24-post pages
        self.type = 'pool'
        self.name = tempdata.get('name')

def getpostcount(query=None):
    """
    Gets the number of posts e621 currently serves.
    If query is specified, gets the number of posts that matches it.
    Returns an integer.
    """
    request = "/post/index.xml?limit=1"
    if query:
        request += "&tags=" + quote(query)
    response = urlopen(SITEADDRESS + request)
    data = ET.parse(response).getroot()
    posts = int(data.get('count'))

    return posts
