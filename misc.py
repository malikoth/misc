#! /usr/bin/env python

import os
import shlex
import subprocess
import textwrap
import time

from ConfigParser import ConfigParser
from collections import OrderedDict

import rumps


DEFAULT_ICON_SIZE = (16, 16)

player_properties = [
    'shuffling',
    'shuffling enabled',
    'repeating',
    'sound volume',
    'player state',
    'player position',
]

track_properties = [
    'name',
    'artist',
    'album',
    'album artist',
    'duration',
    'disc number',
    'played count',
    'track number',
    'popularity',
    'spotify url',
    'id',
]

commands = OrderedDict([
    ('Play', ('play', 'play39.png')),
    ('Pause', ('pause', 'pause14.png')),
    ('Play / Pause', ('playpause', 'play40.png')),
    ('Next track', ('next track', 'step.png')),
    ('Previous track', ('previous track', 'step1.png')),
])


QUERY_STRING = '{' + \
    ', '.join('{}: {}'.format(key.replace(' ', '_'), key) for key in player_properties) + \
    '} & {' + \
    ', '.join('{}: {}'.format(key.replace(' ', '_'), key) for key in track_properties) + \
    '}'


class MISC(rumps.App):
    format_string = '{name:.35} - {album:.35} ({player_position} / {duration})'

    def __init__(self):
        super(MISC, self).__init__(type(self).__name__)

        self.properties = {}
        self.title = ''
        self.icon = 'images/spotify.png'
        self.menu = None

        self.load_settings()
        self.setup_menu()

    @rumps.timer(1)
    def check_status(self, sender):
        try:
            self.properties = {}
            for prop in shlex.split(self._run_osascript(QUERY_STRING).strip('{}')):
                key, _, val = prop.partition(':')
                key = key.replace(' ', '_')
                self.properties[key] = val

            for key in ('duration', 'player_position'):
                self.properties[key] = time.strftime('%M:%S', time.gmtime(float(self.properties[key])))

            if any(map(self.properties['album'].startswith, ('http://', 'https://', 'spotify:'))):
                self.properties['album'] = 'Spotify Ad'

            for key, val in self.properties.items():
                self.menu['Current track'][key].title = '{}: {}'.format(key, val)

            self.menu['Options']['Shuffle'].state = self.properties['shuffling'] == 'true'
            self.menu['Options']['Repeat'].state = self.properties['repeating'] == 'true'
        except Exception:
            raise
        self.title = self.format_string.format(**self.properties)

    def load_settings(self):
        try:
            config = ConfigParser()
            config.readfp(self.open('settings.ini'))
            self.format_string = config.get('options', 'format_string', vars={'format_string': MISC.format_string})
        except:
            pass

    def setup_menu(self):
        self.menu = [
            {'Spotify': ['Version:', 'Launch', 'Quit']},
            {'Current track': track_properties},
            {'Options': ['Format String', None, 'Shuffle', 'Repeat', {
                'Sound Volume': [rumps.MenuItem('{}%'.format(volume),
                                 callback=lambda x: self._run_osascript('set sound volume to {}'.format(x.title[:-1])))
                                 for volume in range(100, -1, -20)]
            }]},
            None,
        ]
        self.menu = [rumps.MenuItem(title, icon=os.path.join('images', action[1]), dimensions=DEFAULT_ICON_SIZE,
                     callback=lambda x: self._run_osascript(commands[x.title][0])) for title, action in commands.items()]
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
        help_text = textwrap.dedent("""
            Enter any string you'd like to be displayed.
            
            The following tokens would be replaced with the listed values for the current track.  
            See the 'Current Track' submenu at any time to see these values while listening.
            
            """) + '\n'.join('{{{}}} - {}'.format(key, val) for key, val in self.properties.items())

        response = rumps.Window(title="Format String", message=help_text, default_text=self.format_string,
                                cancel=True, dimensions=(450, 22)).run()
        if response.clicked:
            self.format_string = response.text.strip()
            config = ConfigParser()
            config.add_section('options')
            config.set('options', 'format_string', self.format_string)
            config.write(self.open('settings.ini', 'w'))

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
        return subprocess.check_output([
            'osascript', '-e',
            'if application "{0}" is running then tell application "{0}" to {1}'.format(application, command)
        ]).strip()


if __name__ == '__main__':
    MISC().run()
