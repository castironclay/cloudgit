import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os


def derive_key_from_passphrase(passphrase: str, salt: bytes) -> bytes:
    """Derive a key from the passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    return key


def encode_bytes_to_base64(b: bytes) -> str:
    """Encode bytes to a base64 string."""
    return base64.b64encode(b).decode("utf-8")


def decode_base64_to_bytes(s: str) -> bytes:
    """Decode a base64 string to bytes."""
    return base64.b64decode(s.encode("utf-8"))


def encrypt_string(passphrase: str, plaintext: str) -> str:
    """Encrypt a plaintext string and return it as a base64 string."""
    salt = os.urandom(16)
    key = derive_key_from_passphrase(passphrase, salt)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plaintext.encode())
    # Prepend salt and encode the combined data as base64
    combined = salt + encrypted
    return encode_bytes_to_base64(combined)


def decrypt_string(passphrase: str, encrypted_base64: str) -> str:
    """Decrypt a base64-encoded encrypted string."""
    combined = decode_base64_to_bytes(encrypted_base64)
    salt = combined[:16]
    encrypted = combined[16:]
    key = derive_key_from_passphrase(passphrase, salt)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted).decode()
    return decrypted
