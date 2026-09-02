from app.crypto.keys import IdentityKeys
from app.schemas.key_bundle import KeyBundleResponse
from app.crypto.handshake import (
    base64_to_bytes, public_key_from_base64, verify_key_bundle,
    initiate_handshake, respond_to_handshake,
)
from app.crypto.ratchet import (
    VeilDoubleRatchet, start_ratchet_as_sender, start_ratchet_as_receiver,
    send_message, receive_message, encode_encrypted_message, decode_encrypted_message,
    x25519_private_to_raw_bytes,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey



async def prepare_first_message(
    my_identity_keys: IdentityKeys,
    peer_bundle: KeyBundleResponse,
    message: bytes,
    associated_data: bytes,
) -> tuple[VeilDoubleRatchet, str]:
    if not verify_key_bundle(peer_bundle):
        raise ValueError("Invalid key bundle signature")

    sk, kem_ciphertext = initiate_handshake(my_identity_keys, peer_bundle)
    peer_x25519_raw = base64_to_bytes(peer_bundle.x25519_public)

    ratchet, encrypted_message = await start_ratchet_as_sender(sk, peer_x25519_raw, message, associated_data)
    return ratchet, encode_encrypted_message(encrypted_message, kem_ciphertext)


async def receive_first_message(
    my_identity_keys: IdentityKeys,
    peer_bundle: KeyBundleResponse,
    encoded_message: str,
    associated_data: bytes,
) -> tuple[VeilDoubleRatchet, bytes]:
    if not verify_key_bundle(peer_bundle):
        raise ValueError("Invalid key bundle signature")

    encrypted_message, kem_ciphertext = decode_encrypted_message(encoded_message)
    if kem_ciphertext is None:
        raise ValueError("Expected an initial message with handshake material")

    peer_x25519_public = public_key_from_base64(peer_bundle.x25519_public, X25519PublicKey)
    sk = respond_to_handshake(my_identity_keys, peer_x25519_public, kem_ciphertext)

    own_ratchet_priv = x25519_private_to_raw_bytes(my_identity_keys.x25519_private)
    return await start_ratchet_as_receiver(sk, own_ratchet_priv, encrypted_message, associated_data)


async def prepare_message(ratchet: VeilDoubleRatchet, message: bytes, associated_data: bytes) -> str:
    encrypted_message = await send_message(ratchet, message, associated_data)
    return encode_encrypted_message(encrypted_message)


async def receive_message_from_string(ratchet: VeilDoubleRatchet, encoded_message: str, associated_data: bytes) -> bytes:
    encrypted_message, _ = decode_encrypted_message(encoded_message)
    return await receive_message(ratchet, encrypted_message, associated_data)