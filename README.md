# OSIRIS PASS

## DECENTRALIZED MULTI-VAULT KEEPER
Developed by @xrlmop

An autonomous password manager utilizing cascade encryption with AES-256-GCM and ChaCha20-Poly1305. The graphical user interface is built on CustomTkinter using fixed-width fonts. The application operates entirely locally, requires no external servers, and does not collect logs.

## Cryptographic Architecture

1. First Layer: AES-256-GCM block cipher.
2. Second Layer: ChaCha20-Poly1305 stream cipher.
3. Key Derivation: PBKDF2HMAC-SHA256 function with 600,000 iterations and a cryptographically secure salt using os.urandom(16).
4. Threading: Database decryption is executed in independent background threading processes to prevent graphical interface locking.

## Deployment Instructions

### macOS (Terminal)
```zsh
git clone [https://github.com/xrlmop/osiris-pass.git]
cd osiris-pass
pip3 install customtkinter cryptography --break-system-packages
python3 main.py
```

### Windows (Command Prompt / CMD)
```bash
git clone [https://github.com/xrlmop/osiris-pass.git]
cd osiris-pass
pip install customtkinter cryptography
python main.py
```

## System Specifications and Features
* Brute-Force Protection: Implementing a cascade key derivation scheme.
* Local Storage: Session data and encrypted vaults are kept within the user's directory in isolated JSON/ENC structures.
* Interface Adaptation: Automatic font selection using Courier (macOS) and Consolas (Windows).
