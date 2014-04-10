#Description

A cross-platform program designed to give the user desktop notifications when the status of specified TwitchTV channels change (eg. They start streaming, update their stream information, or stop streaming).

#Features

* Efficiency:
	* Uses a persistent https connection for the api.
	* Has a cache for user avatars. Will download avatars as needed, and on subsequent runs, it will only re-download an avatar if it is modified (just like the refresh button does on a Web Browser).
	* The program spends the vast majority of its time sleeping, or waiting on IO, so it uses very little CPU time.

* Robustness: 
	* It is designed to recover, by itself, from periods where the internet connection is lost.

#Dependencies

* Versions:
	* **Portable Windows Release**: This version is put together with py2exe and should contain most dependencies. Try it first, and if it doesn't run then try installing the following:
		* The [Microsoft Visual C++ runtime](http://www.microsoft.com/en-us/download/details.aspx?id=29) that the python lib was compiled with.
		* The [GTK+ runtime](http://www.gtk.org/download/index.php)
	* **Standard Release**: This is just the python code. Naturally this version is the easiest to alter. Requirements:
		* [Python 2.7](https://www.python.org/downloads/) (Note for Windows users: You will also have to add python to your path. The easiest method is to go to C:\Python27\lib\tools, double click on win_add2path.py, and restart)
		* [NumPy](http://sourceforge.net/projects/numpy/files/NumPy/)
		* [PIL](http://www.pythonware.com/products/pil/)
		* [pyGtk](http://www.pygtk.org/downloads.html)
		* (Linux only, optional) pynotify (python-notify) or python-notify2

#Set-up

Add the usernames of people which you want channel notifications for to followedList.txt, one per line. Note: You can have blank lines and comments can be created by prefixing a line with #. See example_followedList.txt.

#Running

* Windows:
	double click run.bat

* Linux/Other:
	open a terminal in the folder and run
> python main.py

#Stopping

Just go to the command line/terminal it is running in and press Ctrl+C.

#Technical Notes

The program checks for status updates once every 5 minutes. You can of course decrease this delay by altering CYCLE_SLEEP_TIME in main.py. Testing showed that from the time someone starts streaming, TwitchTV takes about 2 minutes to update their status, so keep that in mind.