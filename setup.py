from setuptools import setup

setup(
    app=['misc.py'],
    name='misc',
    version='0.2',
    packages=[''],
    url='http://github.com/malikoth/misc',
    license='',
    author='Kyle Rich',
    author_email='',
    description='Mac Interface Spotify Client',
    data_files=[],
    options={'py2app': {
        'argv_emulation': True,
        'plist': {
            'LSUIElement': True,
        },
        'packages': ['rumps'],
        'resources': ['images'],
        'iconfile': 'images/spotify.png',
    }},
    setup_requres=['py2app'],
    install_requires=['rumps'],
    dependency_links=['git+https://github.com/jaredks/rumps#egg=rumps']
)
