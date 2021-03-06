#! /usr/bin/env python

import time
from configparser import ConfigParser
from textwrap import dedent
from pathlib import Path

from cached_property import cached_property, cached_property_ttl
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

# TODO: Think of a way to specify longer, shorter, variable length displays, etc.
DEFAULT_FORMAT_STRING = '{name:.50} - {album:.50} ({player position} / {duration})'
DEFAULT_ICON_SIZE = (16, 16)
IMAGE_PATH = Path(__file__).parents[1] / 'images'
PROPERTY_UPDATE_INTERVAL = 1


class MISC(rumps.App):
    def __init__(self):
        # TODO: Submit PR to rumps to convert Path to str
        super().__init__(type(self).__name__, icon=str(IMAGE_PATH / 'spotify.png'))
        self.menu_setup()

    @staticmethod
    def format_time(seconds):
        return time.strftime('%-M:%S', time.gmtime(seconds))

    def send(self, command):
        run(command, 'Spotify')

    @cached_property_ttl(PROPERTY_UPDATE_INTERVAL / 2)
    def properties(self):
        props = get_properties()
        if not props:
            return {}

        props['duration'] = self.format_time(props['duration'] / 1000)
        props['player position'] = self.format_time(props['player position'])
        if any(map(props['album'].startswith, ('http://', 'https://', 'spotify:'))):
            props['album'] = 'Spotify Ad'
        return props

    @cached_property
    def format_string(self):
        return self.config.get('options', 'format_string', vars={'format_string': DEFAULT_FORMAT_STRING})

    @cached_property
    def config(self):
        config = ConfigParser()
        try:
            with self.open('settings.ini') as f:
                config.readfp(f)
        except IOError:
            config.add_section('options')
            config.set('options', 'format_string', DEFAULT_FORMAT_STRING)
        return config

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
        if not self.properties:
            return

        for prop in PLAYER_PROPERTIES:
            self.menu['Spotify'][prop].title = f'{prop}: {self.properties[prop]}'

        for prop in TRACK_PROPERTIES:
            self.menu['Current track'][prop].title = f'{prop}: {self.properties[prop]}'

        self.menu['Shuffle'].state = self.properties['shuffling']
        self.menu['Repeat'].state = self.properties['repeating']

        # TODO: Figure out why this isn't updating the SliderMenuItem
        self.menu['Sound Volume'].value = self.properties['sound volume']

        self.title = self.format_string.format(**self.properties)

    @rumps.clicked('Spotify', 'Launch')
    def launch_spotify(self, sender):
        run('tell app "Spotify" to activate')

    @rumps.clicked('Spotify', 'Quit')
    def quit_spotify(self, sender):
        self.send('quit')

    @rumps.clicked('Format String')
    def format_string_window(self, sender):
        # Including 12 spaces in the LF because the rest of the text has that indentation is a hack
        # TODO: Figure out something better for making indentation consistent and idiomatic
        LF = '\n            '
        help_text = dedent(f"""
            Enter any string you'd like to be displayed.

            The following tokens would be replaced with the listed values
            See the 'Spotify' and 'Current Track' submenus to see these values while listening

            TRACK PROPERTIES:
            {LF.join(f'{{{prop}}} - {self.properties[prop]}' for prop in TRACK_PROPERTIES)}

            PLAYER PROPERTIES:
            {LF.join(f'{{{prop}}} - {self.properties[prop]}' for prop in TRACK_PROPERTIES)}
            """)

        # TODO: Figure out why this text is not editable
        response = rumps.Window(
            title="Format String",
            message=help_text,
            default_text=self.format_string,
            cancel=True,
            dimensions=(450, 22)
        ).run()

        if response.clicked:
            self.format_string = response.text.strip()
            self.config.set('options', 'format_string', self.format_string)
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
