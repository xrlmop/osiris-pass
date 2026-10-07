# 👁️ OSIRIS PASS

> **DECENTRALIZED MULTI-VAULT KEEPER**  
> *Powered by @xrlmop*

Универсальный анонимный менеджер паролей с каскадным шифрованием **AES-256-GCM + ChaCha20-Poly1305** и анимированной заставкой в стиле киберпанк. Полностью совместим с **macOS** и **Windows**.

---

## 🚀 Быстрая установка и запуск (Готовые скрипты)

### 🍏 Для macOS (в Терминале):
```zsh
# 1. Клонировать репозиторий
git clone https://github.com
cd osiris-pass

# 2. Установить зависимости (Homebrew Python 3.14)
pip3 install customtkinter cryptography --break-system-packages

# 3. Запустить систему
python3 main.py
```

### 💻 Для Windows (в Командной строке / CMD):
```bash
# 1. Клонировать репозиторий
git clone https://github.com
cd osiris-pass

# 2. Установить крипто-модули
pip install customtkinter cryptography

# 3. Запустить систему
python main.py
```

---

## 🔒 Безопасность и архитектура
* **Каскадная защита:** Данные шифруются последовательно двумя независимыми алгоритмами.
* **Анонимность:** Программа не требует регистрации, email или личных данных. Всё хранится строго локально на твоем устройстве.
* **Кроссплатформенность:** Автоматическая адаптация пиксельных шрифтов (`Courier` на Mac, `Consolas` на Windows).
