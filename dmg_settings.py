import os

filename = 'OSIRIS_PASS_Installer.dmg'
volume_name = 'OSIRIS PASS'

# Указываем твою неоновую иконку для самого диска .dmg
icon = 'icon.icns'

# Создаем внутри структуру: ярлык запуска и ссылка на систему
files = {
    '/Users/saint/Desktop/OSIRIS_PASS.command': 'OSIRIS PASS.command'
}

symlinks = {
    'Applications': '/Applications'
}

# Красиво расставляем иконки внутри открытого окна .dmg
icon_locations = {
    'OSIRIS PASS.command': (140, 120),
    'Applications': (380, 120)
}

# Настройки отображения окна Apple Finder
window_rect = ((100, 100), (520, 290))
default_view = 'icon-view'
show_icon_preview = False
