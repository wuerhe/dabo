# This serves as a catch-all script for common utilities that may be used
# in lots of places throughout Dabo. Typically, to use a function 'foo()' in
# this file, add the following import statement to your script:
#
#	import dabo.lib.util as util
# 
# Then, in your code, simply call:
#
#	util.foo()

import os
import sys


def reverseText(tx):
	"""Takes a string and returns it reversed. Example:
	
	dUtils.reverseText("Wow, this is so cool!")
		=> returns "!looc os si siht ,woW"
	"""
	return tx[::-1]


def padl(txt, lngth, fill=" "):
	"""Left pads the given string to the given length."""
	txt = str(txt)[:lngth]
	return (fill * (lngth-len(txt)) ) + txt
		

def padr(txt, lngth, fill=" "):
	"""Right pads the given string to the given length."""
	txt = str(txt)[:lngth]
	return txt + (fill * (lngth-len(txt)) )
		

def padc(txt, lngth, fill=" "):
	""" Return string of the specified length, padded with the
	specified fill character equally on the left and right (center
	the string). Default fill character	is space.
	"""
	txt = str(txt)[:lngth]
	# If the difference is odd, the extra character goes on the right
	diff = lngth - len(txt)
	dl = int( diff / 2)
	dr = diff - dl
	
	return (fill * dl) + txt[:lngth] + (fill * dr)


def getUserHomeDirectory():
	"""Return the user's home directory in a platform-portable way.

	If the home directory cannot be determined, return None.
	"""
	# os.path.expanduser should work on all posix systems (*nix, Mac, and some
	# Windows NT setups):
	hd = None
	try:
		hd = os.path.expanduser("~")
	except:
		pass

	# If for some reason the posix function above didn't work, most Linux setups
	# define the environmental variable $HOME, and perhaps this is done sometimes
	# on Mac and Win as well:
	if hd is None:
		hd = os.environ.get("HOME")

	# If we still haven't found a value, Windows tends to define a $USERPROFILE
	# directory, which usually expands to something like
	#	 c:\Documents and Settings\maryjane
	if hd is None:
		hd = os.environ.get("USERPROFILE")

	return hd


def getUserDaboDirectory():
	"""Return the directory where Dabo can save user preference and setting information.

	On *nix, this will be something like /home/pmcnett/.dabo
	On Windows, it will be more like c:\Documents and Settings\pmcnett\Application Data\Dabo

	This function relies on platform conventions to determine this information. If it
	cannot be determined (because platform conventions were circumvented), the return
	value will be None.

	This function will try to create the directory if it doesn't already exist.
	"""
	dd = None
	if sys.platform in ("win32", ):
		dd = os.environ.get("APPDATA")
		if dd is not None:
			dd = os.path.join(dd, "Dabo")

	if dd is None:
		dd = getUserHomeDirectory()

		if dd is not None:
			dd = os.path.join(dd, ".dabo")

	if not os.path.exists(dd):
		# try to create the dabo directory:
		try:
			os.makedirs(dd)
		except:
			print "Couldn't create the .dabo directory (%s)." % dd

	return dd
