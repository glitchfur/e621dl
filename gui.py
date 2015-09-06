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

from urllib import urlretrieve
from urlparse import urlparse
from threading import Thread
from time import sleep
from os import chdir
import Tkinter as tk
import ttk
import Queue

from api import *

import tkMessageBox
import tkFileDialog

import version

ABOUTTEXT = """Copyright (C) 2014, "Glitch"
http://www.glitchfur.net/

This program comes with
ABSOLUTELY NO WARRANTY.
This is free software, and you
are welcome to redistribute it
under certain conditions;
see LICENSE.TXT for details.

Find a bug? Report it on IRC:
http://irc.glitchfur.net/"""

NOQUERY = "You didn't type anything, silly goose!"
NORESULTS = "Nothing matched your query."
LARGEPOST = """You're downloading a large number of posts.
This may take a really long time."""

OPTIONS = {
    # Add a number before each post
    'PREFIXNUM': False,
    # Number of seconds to pause showing status messages
    'SLEEPTIME': 3
    }

class GUInterface:
    def __init__(self, master):
        """
        Constructs the user interface.
        """
        self.root = master
        self.root.title(version.NAME)
        self.root.resizable(False, False)

        self.frame = ttk.Frame(self.root, padding='5')
        self.frame.grid()

        self.title = ttk.Label(self.frame, text=version.NAME, font='bold')
        self.title.grid(column=1, row=1, columnspan=2)

        self.description = ttk.Label(self.frame,
                        text="enter query and post limit below (0 for infinite)")
        self.description.grid(column=1, row=2, columnspan=2)

        self.input = ttk.Frame(self.frame)
        self.input.columnconfigure(1, weight=1)
        self.input.grid(column=1, row=3, sticky='we')

        self.query = ttk.Entry(self.input)
        self.query.bind('<Return>', lambda x: self.submit.invoke())
        self.query.grid(column=1, row=1, sticky='we')
        self.query.focus()

        self.limit = tk.Spinbox(self.input, from_='0', to='256', width='3')
        self.limit.grid(column=2, row=1, padx='2 0', sticky='e')

        self.submit = ttk.Button(self.frame, text='Submit', command=self.onSubmit)
        self.submit.grid(column=2, row=3, padx='6 0')

        self.about = ttk.Button(self.frame, text='About', command=self.aboutDialog)
        self.about.grid(column=2, row=4, padx='6 0')

        self.progress = ttk.Progressbar(self.frame, length='200')
        self.progress.grid(column=1, row=4)

        self.status = ttk.Label(self.frame)
        self.status['text'] = "Welcome!"
        self.status.grid(column=1, row=5, columnspan='2')

        self.go()

    def aboutDialog(self):
        """
        Displays program information.
        """
        tkMessageBox.showinfo(
            title = 'About',
            message = version.NAME + " " + version.VERSION,
            detail = ABOUTTEXT,
            parent = self.root)

    def downloadDialog(self, prompt):
        """
        Presents the user with a Yes/No dialog, asking to initiate a download.
        Returns boolean value.
        """
        reply = tkMessageBox.askyesno(
            title = 'Download',
            message = prompt,
            parent = self.root)

        return reply

    def saveDialog(self):
        """
        Presents the user with a Save dialog, allowing them to pick a directory.
        Returns selected path. Returns None if canceled.
        """
        saveloc = tkFileDialog.askdirectory()
        if saveloc:
            return saveloc
        else:
            return

    def onSubmit(self):
        """
        Contains the commands to be executed when the user clicks "Submit"
        """
        query = self.query.get()
        if not query:
            self.alert('Error', NOQUERY)
            return
        # What's this? An easter egg? :3
        # Well, actually, it's an easter egg within Python itself.
        # I just happened to carry it over here, for the Python-literate people.
        elif query == "import antigravity":
            import antigravity
            return
        try:
            limit = int(self.limit.get())
        except ValueError:
            limit = None
        self.do(('submit', query, limit))

    def onDownload(self, obj):
        """
        Initializes pre-download steps, like asking the user for save location.
        """
        if obj.type == 'query':
            msg = "Going to download %s posts. Proceed?" % \
                                                    ('{:,}'.format(obj.posts))
        elif obj.type == 'pool':
            msg = "Downloading %s posts from pool '%s'. Proceed?" % \
                                        ('{:,}'.format(obj.posts), obj.name)
        if self.downloadDialog(msg):
            if obj.posts > 500:
                tkMessageBox.showinfo(
                    title = "Warning",
                    message = LARGEPOST,
                    parent = self.root)
            saveloc = self.saveDialog()
            if saveloc:
                chdir(saveloc)
            else:
                self.reset()
                return
            self.do(('download', obj))
        else:
            self.reset()

    def do(self, cmd):
        """
        Alias for self.wq.put()
        """
        self.wq.put(cmd)

    def go(self):
        """
        Creates queues, instantiates worker thread, etc.
        """
        self.gq = Queue.Queue()
        self.wq = Queue.Queue()
        self.worker = Worker(self.gq, self.wq)
        self.do(('getposts',))
        self.poll()

    def poll(self):
        """
        Polls the GUI queue for actions to be done and performs said actions.
        """
        while self.gq.qsize():
            try:
                msg = self.gq.get()
            except Queue.Empty:
                pass

            if msg[0] == 'progress':
                # ('progress', attribute, value) with the exception of stop
                if msg[1] == 'value':
                    self.progress['value'] = msg[2]
                elif msg[1] == 'max':
                    self.progress['maximum'] = msg[2]
                elif msg[1] == 'mode':
                    self.progress['mode'] = msg[2]
                elif msg[1] == 'stop':
                    self.progress.stop()
            elif msg[0] == 'busy':
                self.busy()
            elif msg[0] == 'status':
                self.status['text'] = msg[1]
            elif msg[0] == 'reset':
                self.reset()
            elif msg[0] == 'error':
                self.error(msg[1])
            elif msg[0] == 'alert':
                self.alert(msg[1], msg[2])
            elif msg[0] == 'e621string':
                self.e621string = msg[1]
                self.status['text'] = msg[1]
            elif msg[0] == 'predl':
                # ('predl', object)
                self.onDownload(msg[1])

        self.root.after(100, self.poll)

    def alert(self, atitle, amsg):
        """
        Presents the user with a simple message box with an OK button.
        Used to alert the user about something or to provide information.
        Basically a wrapper for tkMessageBox.showinfo
        """
        tkMessageBox.showinfo(
            title = atitle,
            message = amsg,
            parent = self.root)

    def error(self, error):
        """
        Displays an error message to the user if something goes wrong.
        """
        tkMessageBox.showinfo(
            title = "Error",
            message = "An internal error has occurred.",
            detail = error,
            parent = self.root)

    def busy(self):
        """
        Locks all widgets and shows "Processing" status.
        Used to indicate the program is working.
        """
        self.query.state(['disabled'])
        self.about.state(['disabled'])
        self.submit.state(['disabled'])
        self.progress['mode'] = 'indeterminate'
        self.progress.start()
        self.status['text'] = "Processing ..."

    def reset(self):
        """
        Resets the app widgets back to their original state.
        """
        self.query.state(['!disabled'])
        self.about.state(['!disabled'])
        self.submit.state(['!disabled'])
        self.progress.stop()
        self.progress['mode'] = 'determinate'
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.status['text'] = self.e621string

class Worker(Thread):
    def __init__(self, gQueue, wQueue):
        Thread.__init__(self)
        self.gq = gQueue
        self.wq = wQueue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            if self.wq.qsize():
                try:
                    msg = self.wq.get()
                except Queue.Empty:
                    pass
                if msg[0] == 'submit':
                    # ('submit', query, limit)
                    self.processInput(msg[1], msg[2])
                elif msg[0] == 'download':
                    # ('download', object)
                    self.download(msg[1])
                elif msg[0] == 'getposts':
                    try:
                        posts = "e621 - Serving %s posts" % \
                                        ('{:,}'.format(getpostcount()))
                    except IOError:
                        self.do(('alert', 'Error', "You don't appear to have an Internet connection."))
                        self.do(('e621string', "e621 - No connection"))
                        continue
                    except Exception, e:
                        self.do(('error', e))
                        self.do(('e621string', "e621 - No connection"))
                        continue
                    self.do(('e621string', posts))

    def do(self, cmd):
        """
        Alias for self.gq.put()
        """
        self.gq.put(cmd)

    def processInput(self, query, limit):
        """
        Dispatcher function to make certain requests based on user input.
        """
        self.do(('busy',))
        if query.startswith('https://e621.net') or query.startswith('e621.net'):
            url = urlparse(query).path.split('/')
            if url[1] == 'pool' and url[2] == 'show':
                # global PREFIXNUM
                OPTIONS['PREFIXNUM'] = True
                self.do(('predl', Pool(url[3])))
            else:
                self.do(('alert', 'Error', 'Invalid URL'))
                self.do(('reset',))
                return
        else:
            # At this point, assume the user is looking for tags.
            self.do(('predl', Query(query, limit)))

    def download(self, obj):
        """
        Starts the download process.
        """

        pages = []

        self.do(('progress', 'stop'))
        self.do(('progress', 'mode', 'determinate'))
        self.do(('progress', 'max', obj.pages))

        # BEGIN DOWNLOADING PAGES

        pagegen = obj.iter()
        for pagenum in xrange(1, (obj.pages + 1)):
            self.do(('status', "Downloading page %d ..." % pagenum))
            try:
                pages.append(pagegen.next())
            except Exception, e:
                self.do(('error', e))
                self.do(('reset',))
                return
            self.do(('progress', 'value', pagenum))

        self.do(('status', "All pages downloaded!"))
        sleep(OPTIONS['SLEEPTIME'])

        # BEGIN DOWNLOADING POSTS

        loopiter = 1
        self.do(('progress', 'value', 0))
        self.do(('progress', 'max', obj.posts))

        for page in pages:
            # 'posts' tag may or may not be the root tag
            if page.getroot().tag == 'posts':
                posts = page.getroot()
            else:
                posts = page.find('posts')

            for post in posts:
                fileurl = post.get('file_url')
                filename = fileurl.split('/')[-1]
                if OPTIONS['PREFIXNUM']:
                    filename = "Page %d - %s" % (loopiter, filename)
                self.do(('status', "Downloading image %d/%d ..." % (loopiter, obj.posts)))
                try:
                    urlretrieve(fileurl, filename)
                except Exception, e:
                    self.do(('error', e))
                    self.do(('reset',))
                    return
                self.do(('progress', 'value', loopiter))
                if loopiter == obj.posts:
                    break
                loopiter += 1

            if not ((loopiter - 1) % 100):
                for i in xrange(10, 0, -1):
                    self.do(('progress', 'value', 10 - i))
                    self.do(('progress', 'max', 10))
                    self.do(('status', 'Throttling ... %d' % i))
                    sleep(1)

            self.do(('progress', 'value', loopiter))
            self.do(('progress', 'max', obj.posts))

        self.do(('status', "Done! Downloaded %d posts." % obj.posts))
        sleep(OPTIONS['SLEEPTIME'])

        self.do(('reset',))