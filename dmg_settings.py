import os

filename = 'OSIRIS_PASS_Installer.dmg'
volume_name = 'OSIRIS PASS'
icon = 'icon.icns'

files = {
    '/Users/saint/Desktop/OSIRIS_PASS.command': 'OSIRIS PASS.command'
}

symlinks = {
    'Applications': '/Applications'
}

icon_locations = {
    'OSIRIS PASS.command': (140, 120),
    'Applications': (380, 120)
}

window_rect = ((100, 100), (520, 290))
default_view = 'icon-view'
show_icon_preview = False
