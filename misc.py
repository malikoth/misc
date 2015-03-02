# TODO: Persist settings to the app folder settings file
# TODO: Add notification option for displaying new song info
# TODO: Add support for album image to the notification
# TODO: Add better time formatting
# TODO: Attribute icon files correctly
# TODO: Add setup.py to create py2app correctly

import os
import subprocess
import rumps

from collections import OrderedDict
import time


DEFAULT_ICON_SIZE = (16, 16)

attributes = OrderedDict([
    ('song', 'name of current track'),
    ('artist', 'artist of current track'),
    ('album', 'album of current track'),
    ('album_artist', 'album artist of current track'),
    ('position', 'player position'),
    ('duration', 'duration of current track'),
    ('disc', 'disc number of current track'),
    ('count', 'played count of current track'),
    ('num', 'track number of current track'),
    ('rating', 'starred of current track'),
    ('popularity', 'popularity of current track'),
    ('url', 'spotify url of current track'),
    ('id', 'id of current track'),
])

commands = OrderedDict([
    ('Play', ('play', 'play39.png')),
    ('Pause', ('pause', 'pause14.png')),
    ('Play / Pause', ('playpause', 'play40.png')),
    ('Next track', ('next track', 'step.png')),
    ('Previous track', ('previous track', 'step1.png')),
])


class MMSI(rumps.App):
    def __init__(self):
        super(MMSI, self).__init__(type(self).__name__)
        for attr in attributes.keys():
            setattr(self, attr, None)

        self.icon = 'images/spotify.png'
        self.format_string = '{song} - {album} ({position} / {duration})'
        self.shuffle = None
        self.repeat = None
        self.setup_menu()

    @rumps.timer(1)
    def check_status(self, sender):
        try:
            temp = self._run_osascript(attributes['id'])
            if temp != self.id:
                for var, action in attributes.iteritems():
                    setattr(self, var, filter(lambda c: ord(c) < 128, self._run_osascript(action)))

                    if var == 'duration':
                        self.duration = time.strftime('%M:%S', time.gmtime(float(self.duration)))
                    if var == 'rating':
                        self.rating = '' if self.rating == 'false' else '*' * int(self.rating)
                    if var == 'album' and self.album.startswith('http://adclick'):
                        self.album = 'Spotify Ad'
                    self.menu['Current track'][var].title = '{}: {}'.format(var, getattr(self, var))
                self.shuffle = self._run_osascript('shuffling') == 'true'
                self.menu['Options']['Shuffle'].state = self.shuffle
                self.repeat = self._run_osascript('repeating') == 'true'
                self.menu['Options']['Repeat'].state = self.repeat
            if temp == self.id and 'position' in self.format_string:
                self.position = time.strftime('%M:%S', time.gmtime(float(self._run_osascript(attributes['position']))))
                self.menu['Current track']['position'].title = '{}: {}'.format('position', self.position)
        except Exception:
            raise
        self.title = self.format_string.format(**{attr: getattr(self, attr) for attr in attributes.keys()})

    def setup_menu(self):
        self.menu = [
            {'Spotify': ['Version:', 'Launch', 'Quit']},
            {'Current track': attributes.keys()},
            {'Options': ['Format String', None, 'Shuffle', 'Repeat', {
                'Sound Volume': [rumps.MenuItem('{}%'.format(volume),
                                 callback=lambda x: self._run_osascript('set sound volume to {}'.format(x.title[:-1])))
                                 for volume in range(100, -1, -20)]
            }]},
            None,
        ]
        self.menu = [rumps.MenuItem(title, icon=os.path.join('images', action[1]), dimensions=DEFAULT_ICON_SIZE,
                     callback=lambda x: self._run_osascript(commands[x.title][0])) for title, action in commands.iteritems()]
        self.menu.add(None)
        self.menu['Spotify'].set_icon('images/spotify.png', DEFAULT_ICON_SIZE)
        self.menu['Spotify']['Launch'].set_icon('images/power27.png', DEFAULT_ICON_SIZE)
        self.menu['Spotify']['Quit'].set_icon('images/remove11.png', DEFAULT_ICON_SIZE)
        self.menu['Spotify']['Version:'].set_icon('images/question23.png', DEFAULT_ICON_SIZE)
        self.menu['Spotify']['Version:'].title += self._run_osascript('version')
        self.menu['Current track'].set_icon('images/music66.png', DEFAULT_ICON_SIZE)
        self.menu['Options'].set_icon('images/cog2.png', DEFAULT_ICON_SIZE)
        self.menu['Options']['Format String'].set_icon('images/quote2.png', DEFAULT_ICON_SIZE)
        # self.menu['Options']['Notifications'].set_icon('images/<INSERT_HERE>.png', DEFAULT_ICON_SIZE)
        self.menu['Options']['Shuffle'].set_icon('images/couple35.png', DEFAULT_ICON_SIZE)
        self.menu['Options']['Repeat'].set_icon('images/refresh36.png', DEFAULT_ICON_SIZE)
        self.menu['Options']['Sound Volume'].set_icon('images/reduced.png', DEFAULT_ICON_SIZE)

    @rumps.clicked('Spotify', 'Launch')
    def launch_spotify(self, sender):
        self._run_osascript('activate')

    @rumps.clicked('Spotify', 'Quit')
    def quit_spotify(self, sender):
        self._run_osascript('quit')

    @rumps.clicked('Options', 'Format String')
    def set_format_string(self, sender):
        help_text = """
Enter any string you'd like to be displayed.

The following tokens would be replaced with the listed values for the current track.  See the 'Current Track' submenu at any time to see these values while listening

""" + '\n'.join('{{{}}} - {}'.format(attr, getattr(self, attr)) for attr in attributes.keys())

        response = rumps.Window(title="Format String", message=help_text, default_text=self.format_string, cancel=True, dimensions=(450, 22)).run()
        if response.clicked:
            self.format_string = response.text.strip()

    @rumps.clicked('Options', 'Shuffle')
    def set_shuffle(self, sender):
        sender.state = not sender.state
        self._run_osascript('set shuffling to {}'.format(sender.state))

    @rumps.clicked('Options', 'Repeat')
    def set_repeat(self, sender):
        sender.state = not sender.state
        self._run_osascript('set repeating to {}'.format(sender.state))

    @staticmethod
    def _run_osascript(command, application='Spotify'):
        # print 'if application "{0}" is running then tell application "{0}" to {1}'.format(application, command)
        return subprocess.check_output([
            'osascript', '-e',
            'if application "{0}" is running then tell application "{0}" to {1}'.format(application, command)
        ]).strip()


if __name__ == '__main__':
    MMSI().run()
