# Mac Interface Spotify Client (MISC)

## Installation

* Download https://github.com/Jzar/misc/releases/download/v0.1.1/misc.tgz
* Extract, and copy the app to your Applications folder
* See the [Issues with Spotify](https://github.com/Jzar/misc#issues-with-spotify) section
 * Patch and restart Spotify if necessary
* Run MISC

## Overview

Here's my own take on a nice statusbar app to display the current status of Spotify.
It also has commands to let you control Spotify through applescript.

Here's what it looks like most of the time:

![Main Display](https://raw.githubusercontent.com/Jzar/misc/docs/screenshots/MISC_display.png)

Here are the status and control menus:

![Status menu](https://raw.githubusercontent.com/Jzar/misc/docs/screenshots/MISC_menu_1.png)
![Control menu](https://raw.githubusercontent.com/Jzar/misc/docs/screenshots/MISC_menu_2.png)

You can control the format of the text displayed in the statusbar, and apply [Python string formatting](https://docs.python.org/2.7/library/string.html#formatstrings) to it.
You can use all of the variables shown in the 'Current track' menu to display whatever information you want.  Python
string formatting capabilities give you access to alignment, spacing, fill, number, and min and max width for
each field in the format string.  Make it as long or as short as you want, and make it display whatever information you
care about.

(The ability to set this format string is the primary reason I created this instead of using for instance, Statusfy)

![String format dialog](https://raw.githubusercontent.com/Jzar/misc/docs/screenshots/MISC_dialog.png)

## Issues with Spotify

There are at least two known issues with Spotify, as of version 1.0.2.6.g9977a14b.

* Applescript definition file is in the wrong place.  Fix it by following either of the following two links:
 * [Edit the Info.plist file for Spotify](https://www.unifiedremote.com/tutorials/how-to-get-spotify-version-spotify-101xxx-on-mac-osx)
 * [Move the Spotify.sdef file back to its original location](http://www.executionunit.com/blog/2015/03/21/spotify-applescript-is-broken/)
* 'Player position' variable doesn't update correctly while playing
 * This worked great until the 1.x update to Spotify, and now it only updates when you pause Spotify.  This is not
   my fault, and there's nothing I can do about it.  Go complain on the Spotify forum and tell them to get their
   act together!
