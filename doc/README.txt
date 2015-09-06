e621 Downloader
Copyright (C) 2014, "Glitch"
http://www.glitchfur.net/

INTRODUCTION
============
This program allows you to mass-download images from the e621.net website based
on a tag (or multiple tags) that you enter into the search field.

More information can be found at http://www.glitchfur.net/apps/e621dl

HOW TO USE
==========
* Windows (.exe)
	If you downloaded the Windows (.exe) version of this application, simply
	double-click the e621dl.exe executable to run it. You may find it
	convenient to make a shortcut to this file on your Desktop.

* Mac OS X, Linux, etc. (.py)
	If you downloaded the source code (.py) version of this application, you
	must be comfortable using the Terminal/Command Prompt in your OS. In
	addition you must have Python 2 installed.

	Within a terminal window, change your working directory to the location
	of e621dl.py and then run this command:

	python e621dl.py

	If you have multiple versions of Python installed on your system, you may
	need to run this instead:

	python2 e621dl.py

COMPILING INTO AN .EXE (WINDOWS)
================================
This program can be compiled into an executable file, which can be run on other
computers running Windows without Python having to be installed. To do this,
you will need the most recent version of Python 2 and py2exe 0.6.9.

Once you have those installed and configured properly, compiling is very easy.
Open a Command Prompt on your machine, change your working directory to the
location of setup.py (contained in this package) and run:

	python setup.py py2exe

The code and all required packages will be "packed" into an .exe form, located
in the "dist" folder. Once it's complete, you will be able to run this program
without a Python installation by running the executable.

IMPORTANT NOTE: When transferring the compiled version to another computer, you
must copy the ENTIRE "dist" folder. Otherwise, the application will not have
the files it needs to run, and will fail to start.
