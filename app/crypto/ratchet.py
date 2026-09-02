from doubleratchet import DoubleRatchet as DR, Header, EncryptedMessage
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
from doubleratchet.recommended import (
    aead_aes_hmac,
    diffie_hellman_ratchet_curve25519 as dhr25519,
    HashFunction,
    kdf_hkdf,
    kdf_separate_hmacs,
)
import json
from app.crypto.handshake import bytes_to_base64, base64_to_bytes


class VeilDoubleRatchet(DR):
    @staticmethod
    def _build_associated_data(associated_data: bytes, header: Header) -> bytes:
        return (
            associated_data
            + header.ratchet_pub
            + header.sending_chain_length.to_bytes(8, "big")
            + header.previous_sending_chain_length.to_bytes(8, "big")
        )


class VeilDiffieHellmanRatchet(dhr25519.DiffieHellmanRatchet):
    pass


class VeilAEAD(aead_aes_hmac.AEAD):
    @staticmethod
    def _get_hash_function() -> HashFunction:
        return HashFunction.SHA_256

    @staticmethod
    def _get_info() -> bytes:
        return b"Veil AEAD"


class VeilRootChainKDF(kdf_hkdf.KDF):
    @staticmethod
    def _get_hash_function() -> HashFunction:
        return HashFunction.SHA_256

    @staticmethod
    def _get_info() -> bytes:
        return b"Veil Root Chain KDF"


class VeilMessageChainKDF(kdf_separate_hmacs.KDF):
    @staticmethod
    def _get_hash_function() -> HashFunction:
        return HashFunction.SHA_256

    
RATCHET_CONFIG = {
    "diffie_hellman_ratchet_class": VeilDiffieHellmanRatchet,
    "root_chain_kdf": VeilRootChainKDF,
    "message_chain_kdf": VeilMessageChainKDF,
    "message_chain_constant": b"\x01\x02",
    "dos_protection_threshold": 100,
    "max_num_skipped_message_keys": 1000,
    "aead": VeilAEAD,
}


def x25519_public_to_raw_bytes(public_key: X25519PublicKey) -> bytes:
    return public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)


def x25519_private_to_raw_bytes(private_key: X25519PrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=Encoding.Raw, format=PrivateFormat.Raw, encryption_algorithm=NoEncryption()
    )

async def start_ratchet_as_sender(
    shared_secret: bytes,
    recipient_ratchet_pub: bytes,
    message: bytes,
    associated_data: bytes,
):
    return await VeilDoubleRatchet.encrypt_initial_message(
        shared_secret=shared_secret,
        recipient_ratchet_pub=recipient_ratchet_pub,
        message=message,
        associated_data=associated_data,
        **RATCHET_CONFIG,
    )

async def start_ratchet_as_receiver(
    shared_secret: bytes,
    own_ratchet_priv: bytes,
    message,
    associated_data: bytes,
):
    return await VeilDoubleRatchet.decrypt_initial_message(
        shared_secret=shared_secret,
        own_ratchet_priv=own_ratchet_priv,
        message=message,
        associated_data=associated_data,
        **RATCHET_CONFIG,
    )

async def send_message(ratchet: VeilDoubleRatchet, message: bytes, associated_data: bytes):
    return await ratchet.encrypt_message(message, associated_data)

async def receive_message(ratchet: VeilDoubleRatchet, message, associated_data: bytes) -> bytes:
    return await ratchet.decrypt_message(message, associated_data)

def encode_encrypted_message(encrypted_message: EncryptedMessage, kem_ciphertext: bytes | None = None) -> str:
    envelope = {
        "ratchet_pub": bytes_to_base64(encrypted_message.header.ratchet_pub),
        "previous_sending_chain_length": encrypted_message.header.previous_sending_chain_length,
        "sending_chain_length": encrypted_message.header.sending_chain_length,
        "ciphertext": bytes_to_base64(encrypted_message.ciphertext),
        "kem_ciphertext": bytes_to_base64(kem_ciphertext) if kem_ciphertext is not None else None,
    }
    return json.dumps(envelope)


def decode_encrypted_message(data: str) -> tuple[EncryptedMessage, bytes | None]:
    envelope = json.loads(data)
    header = Header(
        ratchet_pub=base64_to_bytes(envelope["ratchet_pub"]),
        previous_sending_chain_length=envelope["previous_sending_chain_length"],
        sending_chain_length=envelope["sending_chain_length"],
    )
    encrypted_message = EncryptedMessage(header=header, ciphertext=base64_to_bytes(envelope["ciphertext"]))
    kem_ciphertext = base64_to_bytes(envelope["kem_ciphertext"]) if envelope["kem_ciphertext"] is not None else None
    return encrypted_message, kem_ciphertext







