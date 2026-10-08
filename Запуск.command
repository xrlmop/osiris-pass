#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    echo "Первоначальная настройка OSIRIS PASS..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install customtkinter cryptography
fi
if [ -f "main.py" ]; then ./venv/bin/python3 main.py; else ./venv/bin/python3 *.py; fi
