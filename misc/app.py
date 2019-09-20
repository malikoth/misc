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


COMMANDS = {
    'Play': 'play',
    'Pause': 'pause',
    'Play / Pause': 'playpause',
    'Next track': 'next track',
    'Previous track': 'previous track',
}
ICONS = {
    ('Spotify', 'Launch'): 'power27.png',
    ('Spotify', 'Quit'): 'remove11.png',
    ('Spotify', 'version'): 'question23.png',

    'Current track': 'music66.png',
    'Format String': 'quote2.png',
    'Shuffle': 'couple35.png',
    'Repeat': 'refresh36.png',
    'Sound Volume': 'reduced.png',

    'Play': 'play39.png',
    'Pause': 'pause14.png',
    'Play / Pause': 'play40.png',
    'Next track': 'step.png',
    'Previous track': 'step1.png',
}
DEFAULT_FORMAT_STRING = '{name:.30} - {album:.25} ({player position} / {duration})'
DEFAULT_ICON_SIZE = (16, 16)
IMAGE_PATH = Path().parent / 'images'
PROPERTY_UPDATE_INTERVAL = 1


class MISC(rumps.App):
    def __init__(self):
        self._last_updated = 0

        # TODO: Remove these private property backing vars, replace with @cached_property in Python3.8
        self._config = None
        self._format_string = None
        self._properties = None

        # TODO: Submit PR to rumps to convert Path to str
        super().__init__(type(self).__name__, icon=str(IMAGE_PATH / 'spotify.png'))
        self.menu_setup()

    @staticmethod
    def format_time(seconds):
        return time.strftime('%-M:%S', time.gmtime(seconds))

    def send(self, command):
        run(command, 'Spotify')

    @property
    def properties(self):
        if not self._properties or time.monotonic() - self._last_updated > PROPERTY_UPDATE_INTERVAL / 2:
            props = get_properties()
            props['duration'] = self.format_time(props['duration'] / 1000)
            props['player position'] = self.format_time(props['player position'])
            if any(map(props['album'].startswith, ('http://', 'https://', 'spotify:'))):
                props['album'] = 'Spotify Ad'
            self._properties = props
            self._last_updated = time.monotonic()
        return self._properties

    @property
    def format_string(self):
        if self._format_string is None:
            self._format_string = self.config.get(
                'options', 'format_string', vars={'format_string': DEFAULT_FORMAT_STRING})
        return self._format_string

    @format_string.setter
    def format_string_setter(self, value):
        self._format_string = value
        self.config.set('options', 'format_string', self.format_string)

    @property
    def config(self):
        if not self._config:
            config = ConfigParser()
            try:
                with self.open('settings.ini') as f:
                    config.readfp(f)
            except IOError:
                config.add_section('options')
                config.set('options', 'format_string', DEFAULT_FORMAT_STRING)
            self._config = config
        return self._config

    def config_save(self):
        with self.open('settings.ini', 'w') as f:
            self.config.write(f)

    def get_menuitem(self, path):
        if isinstance(path, str):
            path = (path,)
        menu = self.menu
        for element in path:
            menu = menu[element]
        return menu

    def menu_setup(self):
        self.menu = [
            {'Spotify': ['Launch', 'Quit', None] + PLAYER_PROPERTIES},
            {'Current track': TRACK_PROPERTIES},
            'Format String', None, 'Shuffle', 'Repeat', 'Sound Volume', None,
            *COMMANDS.keys(), None
        ]

        for title, action in COMMANDS.items():
            self.menu[title].set_callback(lambda sender: self.send(COMMANDS[sender.title]))

        for menu_path, icon in ICONS.items():
            menu = self.get_menuitem(menu_path)
            menu.set_icon(str(IMAGE_PATH / icon), dimensions=DEFAULT_ICON_SIZE, template=True)

    @rumps.timer(1)
    def update_properties(self, sender):
        for prop in PLAYER_PROPERTIES:
            self.menu['Spotify'][prop].title = f'{prop}: {self.properties[prop]}'

        for prop in TRACK_PROPERTIES:
            self.menu['Current track'][prop].title = f'{prop}: {self.properties[prop]}'

        self.menu['Shuffle'].state = self.properties['shuffling']
        self.menu['Repeat'].state = self.properties['repeating']

        # TODO: Figure out why this isn't updating the SliderMenuItem
        self.menu['Sound Volume'].value = self.properties['sound volume']

        self.title = self.format_string.format(**self.properties)

    # TODO: Figure out why this doesn't launch Spotify
    @rumps.clicked('Spotify', 'Launch')
    def launch_spotify(self, sender):
        run('tell app "Spotify" to activate')

    @rumps.clicked('Spotify', 'Quit')
    def quit_spotify(self, sender):
        self.send('quit')

    @rumps.clicked('Format String')
    def format_string_window(self, sender):
        help_text = dedent("""
            Enter any string you'd like to be displayed.

            The following tokens would be replaced with the listed values
            See the 'Spotify' and 'Current Track' submenus to see these values while listening

            """)
        help_text += '\n'.join(f'{{{prop}}} - {self.properties[prop]}' for prop in TRACK_PROPERTIES)

        response = rumps.Window(
            title="Format String",
            message=help_text,
            default_text=self.format_string,
            cancel=True,
            dimensions=(450, 22)
        ).run()

        if response.clicked:
            self.format_string = response.text.strip()
            self.config_save()

    @rumps.clicked('Shuffle')
    def set_shuffle(self, sender):
        sender.state = not sender.state
        self.send(f'set shuffling to {sender.state}')

    @rumps.clicked('Repeat')
    def set_repeat(self, sender):
        sender.state = not sender.state
        self.send(f'set repeating to {sender.state}')

    @rumps.slider('Sound Volume')
    def set_volume(self, sender):
        self.send(f'set sound volume to {sender.value}')


if __name__ == '__main__':
    MISC().run()
