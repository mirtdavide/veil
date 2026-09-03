
import os
import hmac
import hashlib
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

@dataclass
class SenderKey:
    chain_key: bytes
    signature_private: Ed25519PrivateKey
    signature_public: Ed25519PublicKey

@dataclass
class RemoteSenderKey:
    chain_key: bytes
    signature_public: Ed25519PublicKey

def generate_sender_key() -> SenderKey:
    chain_key = os.urandom(32)
    signature_private = Ed25519PrivateKey.generate()
    signature_public = signature_private.public_key()
    return SenderKey(chain_key=chain_key, signature_private=signature_private, signature_public=signature_public)



def advance_chain_key(chain_key: bytes) -> tuple[bytes, bytes]:
    message_key = hmac.new(chain_key, b"\x01", hashlib.sha256).digest()
    next_chain_key = hmac.new(chain_key, b"\x02", hashlib.sha256).digest()
    return message_key, next_chain_key


def derive_encryption_material(message_key: bytes) -> tuple[bytes, bytes]:
    okm = HKDF(algorithm=hashes.SHA256(), length=48, salt=None, info=b"Veil Sender Key Message").derive(message_key)
    return okm[:32], okm[32:]



def encrypt_group_message(sender_key: SenderKey, message: bytes) -> tuple[bytes, bytes]:
    message_key, next_chain_key = advance_chain_key(sender_key.chain_key)
    sender_key.chain_key = next_chain_key

    aes_key, iv = derive_encryption_material(message_key)

    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_message = padder.update(message) + padder.finalize()

    encryptor = Cipher(algorithms.AES(aes_key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(padded_message) + encryptor.finalize()

    signature = sender_key.signature_private.sign(ciphertext)
    return ciphertext, signature

def decrypt_group_message(sender_key: SenderKey, ciphertext: bytes, signature: bytes) -> bytes:
    sender_key.signature_public.verify(signature, ciphertext)

    message_key, next_chain_key = advance_chain_key(sender_key.chain_key)
    sender_key.chain_key = next_chain_key

    aes_key, iv = derive_encryption_material(message_key)

    decryptor = Cipher(algorithms.AES(aes_key), modes.CBC(iv)).decryptor()
    padded_message = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    return unpadder.update(padded_message) + unpadder.finalize()



def serialize_sender_key(sender_key: SenderKey) -> bytes:
    signature_public_raw = sender_key.signature_public.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
    return sender_key.chain_key + signature_public_raw


def deserialize_remote_sender_key(data: bytes) -> RemoteSenderKey:
    chain_key = data[:32]
    signature_public = Ed25519PublicKey.from_public_bytes(data[32:])
    return RemoteSenderKey(chain_key=chain_key, signature_public=signature_public)

CHAT_MESSAGE_TYPE = b"\x00"
SENDER_KEY_MESSAGE_TYPE = b"\x01"


def wrap_chat_message(text: bytes) -> bytes:
    return CHAT_MESSAGE_TYPE + text


def wrap_sender_key_message(sender_key: SenderKey) -> bytes:
    return SENDER_KEY_MESSAGE_TYPE + serialize_sender_key(sender_key)


def unwrap_pairwise_message(data: bytes) -> tuple[str, bytes | RemoteSenderKey]:
    message_type, payload = data[:1], data[1:]
    if message_type == CHAT_MESSAGE_TYPE:
        return "chat", payload
    if message_type == SENDER_KEY_MESSAGE_TYPE:
        return "sender_key", deserialize_remote_sender_key(payload)
    raise ValueError(f"Unknown pairwise message type: {message_type!r}")