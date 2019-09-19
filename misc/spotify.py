import json

from applescript import run, to_json, build_command, Element

TRACK_PROPERTIES = [
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

PLAYER_PROPERTIES = [
    'repeating',
    'sound volume',
    'shuffling',
    'player state',
    'player position',
    'shuffling enabled',
]

CURRENT_TRACK='current track'

GET_PROPERTIES_COMMAND = build_command('Spotify',
    Element('repeating'),
    Element('sound volume'),
    Element('shuffling'),
    Element('player state', quote=True),
    Element('player position'),
    Element('shuffling enabled'),
    Element('artist', of=CURRENT_TRACK, quote=True),
    Element('album', of=CURRENT_TRACK, quote=True),
    Element('disc number', of=CURRENT_TRACK),
    Element('duration', of=CURRENT_TRACK),
    Element('played count', of=CURRENT_TRACK),
    Element('track number', of=CURRENT_TRACK),
    Element('popularity', of=CURRENT_TRACK),
    Element('id', of=CURRENT_TRACK, quote=True),
    Element('name', of=CURRENT_TRACK, quote=True),
    Element('artwork url', of=CURRENT_TRACK, quote=True),
    Element('album artist', of=CURRENT_TRACK, quote=True),
    Element('spotify url', of=CURRENT_TRACK, quote=True),
    Element('version', quote=True),
)


def get_properties():
    return json.loads(to_json(run(GET_PROPERTIES_COMMAND)))


if __name__ == "__main__":
    print(json.dumps(get_properties(), indent=2))
