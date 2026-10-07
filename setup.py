from setuptools import setup

APP = ['main.py']
DATA_FILES = [('', ['backend.py'])]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'OSIRIS PASS',
        'CFBundleDisplayName': 'OSIRIS PASS',
        'CFBundleIdentifier': 'com.xrlmop.osirispass',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
    },
    'includes': ['customtkinter', 'cryptography', 'backend'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
