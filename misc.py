import os
import subprocess
import rumps

from collections import OrderedDict
import time


DEFAULT_ICON_SIZE = (16, 16)

track_properties = [
    'name',
    'artist',
    'album',
    'album artist',
    'player position',
    'duration',
    'disc number',
    'played count',
    'track number',
    'starred',
    'popularity',
    'spotify url',
    'id',
]

player_properties = [
    'shuffling enabled',
    'shuffling',
    'class',
    'repeating',
    'current track',
    'sound volume',
    'player state',
    'artwork',
]

commands = OrderedDict([
    ('Play', ('play', 'play39.png')),
    ('Pause', ('pause', 'pause14.png')),
    ('Play / Pause', ('playpause', 'play40.png')),
    ('Next track', ('next track', 'step.png')),
    ('Previous track', ('previous track', 'step1.png')),
])

character_subs = {
    226: 34,
    195: 'e',
    # 174: '(R)'
}


def _replace_chars(unsafe):
    return ''.join((chr(character_subs[ord(c)]) if isinstance(character_subs[ord(c)], int) else
                   character_subs[ord(c)]) if ord(c) in character_subs else c if ord(c) < 128 else '' for c in unsafe)


class MMSI(rumps.App):
    def __init__(self):
        super(MMSI, self).__init__(type(self).__name__)
        self.properties = {}
        self.icon = 'images/spotify.png'
        self.format_string = '{name:.35} - {album:.35} ({player position} / {duration})'
        self.setup_menu()

    @rumps.timer(1)
    def check_status(self, sender):
        try:
            props = self._run_osascript('get {get properties, get properties of current track}').split(', ')
            for prop in props:
                prop = _replace_chars(prop)
                if any(map(prop.startswith, track_properties + player_properties)):
                    key, _, val = prop.partition(':')
                    if key in ('duration', 'player position'):
                        val = time.strftime('%M:%S', time.gmtime(float(val)))
                    if key == 'starred':
                        val = '' if val == 'false' else '*' * int(val)
                    if key == 'album' and any(map(val.startswith, ('http://', 'https://', 'spotify:'))):
                        val = 'Spotify Ad'
                    self.properties[key] = val
                    last_key = key
                else:
                    self.properties[last_key] += ', ' + prop

            for prop in track_properties:
                    self.menu['Current track'][prop].title = '{}: {}'.format(prop, self.properties[prop])

            self.menu['Options']['Shuffle'].state = self.properties['shuffling'] == 'true'
            self.menu['Options']['Repeat'].state = self.properties['repeating'] == 'true'
        except Exception:
            raise
        self.title = self.format_string.format(**{prop: self.properties[prop] for prop in track_properties})

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

""" + '\n'.join('{{{}}} - {}'.format(prop, self.properties[prop]) for prop in track_properties)

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
