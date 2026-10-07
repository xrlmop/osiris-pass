import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_INDEX_FILE = os.path.join(BASE_DIR, "accounts.json")

def get_file_name(account_id: str) -> str:
    return os.path.join(BASE_DIR, f"vault_{account_id}.enc")

def get_saved_accounts() -> list:
    if not os.path.exists(ACCOUNTS_INDEX_FILE):
        return []
    try:
        with open(ACCOUNTS_INDEX_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except Exception:
        return []

def add_account_to_index(account_id: str):
    accounts = get_saved_accounts()
    if account_id not in accounts:
        accounts.append(account_id)
        try:
            with open(ACCOUNTS_INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump(accounts, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

def delete_account_from_system(account_id: str):
    accounts = get_saved_accounts()
    if account_id in accounts:
        accounts.remove(account_id)
        try:
            with open(ACCOUNTS_INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump(accounts, f, indent=4, ensure_ascii=False)
        except Exception:
            pass
    
    file_path = get_file_name(account_id)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

def generate_double_keys(master_password: str, salt: bytes) -> tuple:
    kdf_aes = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt + b"_aes_layer",
        iterations=600_000,
    )
    key_aes = kdf_aes.derive(master_password.encode())
    
    kdf_chacha = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt + b"_chacha_layer",
        iterations=600_000,
    )
    key_chacha = kdf_chacha.derive(master_password.encode())
    
    return key_aes, key_chacha

def load_vault(account_id: str, master_password: str):
    file_path = get_file_name(account_id)
    if not os.path.exists(file_path):
        return {}, os.urandom(16)
        
    try:
        with open(file_path, "rb") as f:
            salt = f.read(16)
            nonce_chacha = f.read(12)
            nonce_aes = f.read(12)
            encrypted_data = f.read()
            
        key_aes, key_chacha = generate_double_keys(master_password, salt)
        
        chacha = ChaCha20Poly1305(key_chacha)
        inner_encrypted = chacha.decrypt(nonce_chacha, encrypted_data, account_id.encode())
        
        aesgcm = AESGCM(key_aes)
        decrypted_bytes = aesgcm.decrypt(nonce_aes, inner_encrypted, account_id.encode())
        
        return json.loads(decrypted_bytes.decode("utf-8")), salt
    except Exception:
        return None, None

def save_vault(account_id: str, master_password: str, salt: bytes, vault_data: dict):
    file_path = get_file_name(account_id)
    try:
        key_aes, key_chacha = generate_double_keys(master_password, salt)
        nonce_aes = os.urandom(12)
        nonce_chacha = os.urandom(12)
        
        serialized_data = json.dumps(vault_data).encode("utf-8")
        
        aesgcm = AESGCM(key_aes)
        inner_encrypted = aesgcm.encrypt(nonce_aes, serialized_data, account_id.encode())
        
        chacha = ChaCha20Poly1305(key_chacha)
        final_encrypted = chacha.encrypt(nonce_chacha, inner_encrypted, account_id.encode())
        
        with open(file_path, "wb") as f:
            f.write(salt)
            f.write(nonce_chacha)
            f.write(nonce_aes)
            f.write(final_encrypted)
            
        add_account_to_index(account_id)
    except Exception:
        pass
