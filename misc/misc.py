#! /usr/bin/env python

import os
import subprocess
import time
from configparser import ConfigParser
from textwrap import dedent
from pathlib import Path

import rumps

from spotify import get_properties, TRACK_PROPERTIES, PLAYER_PROPERTIES
from applescript import run


IMAGE_PATH = Path('..') / 'images'
DEFAULT_ICON_SIZE = (16, 16)
COMMANDS = {
    'Play': ('play', 'play39.png'),
    'Pause': ('pause', 'pause14.png'),
    'Play / Pause': ('playpause', 'play40.png'),
    'Next track': ('next track', 'step.png'),
    'Previous track': ('previous track', 'step1.png'),
}


class MISC(rumps.App):
    format_string = '{name:.35} - {album:.35} ({player position} / {duration})'

    def __init__(self):
        super().__init__(type(self).__name__)
        self.properties = {}
        self.update_properties()
        self.icon = str(IMAGE_PATH / 'spotify.png')
        self.load_config()
        self.setup_menu()

    @staticmethod
    def format_time(seconds):
        return time.strftime('%M:%S', time.gmtime(seconds))

    def send(self, command):
        run(command, 'Spotify')

    def update_properties(self):
        props = get_properties()
        props['duration'] = self.format_time(props['duration'])
        props['player position'] = self.format_time(props['player position'])
        if any(map(props['album'].startswith, ('http://', 'https://', 'spotify:'))):
            props['album'] = 'Spotify Ad'
        self.properties = props

    @rumps.timer(1)
    def update_menu(self, sender):
        self.update_properties()

        for prop in TRACK_PROPERTIES:
            self.menu['Current track'][prop].title = '{}: {}'.format(prop, self.properties[prop])

        self.menu['Options']['Shuffle'].state = self.properties['shuffling']
        self.menu['Options']['Repeat'].state = self.properties['repeating']

        self.title = self.format_string.format(**{prop: self.properties[prop] for prop in TRACK_PROPERTIES})

    def load_config(self):
        try:
            config = ConfigParser()
            config.readfp(self.open('settings.ini'))
            self.format_string = config.get('options', 'format_string', vars={'format_string': self.format_string})
        except:
            pass

    def save_config(self):
        config = ConfigParser()
        config.add_section('options')
        config.set('options', 'format_string', self.format_string)
        config.write(self.open('settings.ini', 'w'))

    def setup_menu(self):
        self.menu = [
            {'Spotify': ['Version:', 'Launch', 'Quit']},
            {'Current track': TRACK_PROPERTIES},
            {'Options': ['Format String', None, 'Shuffle', 'Repeat', {
                'Sound Volume': [rumps.MenuItem('{}%'.format(volume),
                                 callback=lambda x: self.send('set sound volume to {}'.format(x.title[:-1])))
                                 for volume in range(100, -1, -10)]
            }]},
            None,
        ]
        self.menu = [rumps.MenuItem(title, icon=str(IMAGE_PATH / action[1]), dimensions=DEFAULT_ICON_SIZE,
                     callback=lambda x: self.send(COMMANDS[x.title][0])) for title, action in COMMANDS.items()]
        self.menu.add(None)
        self.menu['Spotify'].set_icon(self.icon, DEFAULT_ICON_SIZE)
        self.menu['Spotify']['Launch'].set_icon(str(IMAGE_PATH / 'power27.png'), DEFAULT_ICON_SIZE)
        self.menu['Spotify']['Quit'].set_icon(str(IMAGE_PATH / 'remove11.png'), DEFAULT_ICON_SIZE)
        self.menu['Spotify']['Version:'].set_icon(str(IMAGE_PATH / 'question23.png'), DEFAULT_ICON_SIZE)
        self.menu['Spotify']['Version:'].title += self.properties['version']
        self.menu['Current track'].set_icon(str(IMAGE_PATH / 'music66.png'), DEFAULT_ICON_SIZE)
        self.menu['Options'].set_icon(str(IMAGE_PATH / 'cog2.png'), DEFAULT_ICON_SIZE)
        self.menu['Options']['Format String'].set_icon(str(IMAGE_PATH / 'quote2.png'), DEFAULT_ICON_SIZE)
        self.menu['Options']['Shuffle'].set_icon(str(IMAGE_PATH / 'couple35.png'), DEFAULT_ICON_SIZE)
        self.menu['Options']['Repeat'].set_icon(str(IMAGE_PATH / 'refresh36.png'), DEFAULT_ICON_SIZE)
        self.menu['Options']['Sound Volume'].set_icon(str(IMAGE_PATH / 'reduced.png'), DEFAULT_ICON_SIZE)

    @rumps.clicked('Spotify', 'Launch')
    def launch_spotify(self, sender):
        self.send('activate')

    @rumps.clicked('Spotify', 'Quit')
    def quit_spotify(self, sender):
        self.send('quit')

    @rumps.clicked('Options', 'Format String')
    def set_format_string(self, sender):
        help_text = dedent("""
            Enter any string you'd like to be displayed.

            The following tokens would be replaced with the listed values for the current track.
            See the 'Current Track' submenu at any time to see these values while listening

            """)
        help_text += '\n'.join('{{{}}} - {}'.format(prop, self.properties[prop]) for prop in TRACK_PROPERTIES)

        response = rumps.Window(
            title="Format String",
            message=help_text,
            default_text=self.format_string,
            cancel=True,
            dimensions=(450, 22)
            ).run()

        if response.clicked:
            self.format_string = response.text.strip()
            self.save_config()

    @rumps.clicked('Options', 'Shuffle')
    def set_shuffle(self, sender):
        sender.state = not sender.state
        self.send('set shuffling to {}'.format(sender.state))

    @rumps.clicked('Options', 'Repeat')
    def set_repeat(self, sender):
        sender.state = not sender.state
        self.send('set repeating to {}'.format(sender.state))


if __name__ == '__main__':
    MISC().run()
