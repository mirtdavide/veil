"""
Versione pytest di scripts/test_group_sender_keys.py.
"""
import pytest
from cryptography.exceptions import InvalidSignature

from app.crypto.keys import generate_identity_keys
from app.crypto.handshake import prepare_key_bundle
from app.schemas.key_bundle import KeyBundleResponse
from app.crypto.conversation import (
    prepare_first_message,
    receive_first_message,
    prepare_message,
    receive_message_from_string,
)
from app.crypto.sender_keys import (
    generate_sender_key,
    encrypt_group_message,
    decrypt_group_message,
    wrap_sender_key_message,
    unwrap_pairwise_message,
)


def bundle_response_from_identity(user_id: int, identity_keys) -> KeyBundleResponse:
    publish = prepare_key_bundle(identity_keys)
    return KeyBundleResponse(user_id=user_id, **publish.model_dump())


class Member:
    def __init__(self, name: str, user_id: int):
        self.name = name
        self.user_id = user_id
        self.identity_keys = generate_identity_keys()
        self.bundle: KeyBundleResponse | None = None
        self.sender_key = generate_sender_key()
        self.pairwise_ratchets: dict[str, object] = {}
        self.remote_sender_keys: dict[str, object] = {}


async def exchange_sender_keys(a: Member, b: Member, associated_data: bytes) -> None:
    a_ratchet, encoded = await prepare_first_message(
        a.identity_keys, b.bundle, wrap_sender_key_message(a.sender_key), associated_data
    )
    a.pairwise_ratchets[b.name] = a_ratchet

    b_ratchet, plaintext = await receive_first_message(
        b.identity_keys, a.bundle, encoded, associated_data
    )
    b.pairwise_ratchets[a.name] = b_ratchet
    kind, payload = unwrap_pairwise_message(plaintext)
    assert kind == "sender_key"
    b.remote_sender_keys[a.name] = payload

    encoded_reply = await prepare_message(b_ratchet, wrap_sender_key_message(b.sender_key), associated_data)
    plaintext_reply = await receive_message_from_string(a_ratchet, encoded_reply, associated_data)
    kind, payload = unwrap_pairwise_message(plaintext_reply)
    assert kind == "sender_key"
    a.remote_sender_keys[b.name] = payload


@pytest.mark.asyncio
async def test_group_sender_keys_end_to_end():
    mario = Member("Mario", 1)
    gianni = Member("Gianni", 2)
    luca = Member("Luca", 3)
    members = [mario, gianni, luca]

    for member in members:
        member.bundle = bundle_response_from_identity(member.user_id, member.identity_keys)

    associated_data = b"gruppo-mario-gianni-luca"

    await exchange_sender_keys(mario, gianni, associated_data)
    await exchange_sender_keys(mario, luca, associated_data)
    await exchange_sender_keys(gianni, luca, associated_data)

    # Mario scrive nel gruppo, letto da entrambi
    ciphertext, signature = encrypt_group_message(mario.sender_key, b"Ciao a tutti citrulli")
    for receiver in (gianni, luca):
        plaintext = decrypt_group_message(receiver.remote_sender_keys["Mario"], ciphertext, signature)
        assert plaintext == b"Ciao a tutti citrulli"

    # Secondo messaggio di Mario: la catena avanza
    ciphertext, signature = encrypt_group_message(mario.sender_key, b"Come va?")
    for receiver in (gianni, luca):
        plaintext = decrypt_group_message(receiver.remote_sender_keys["Mario"], ciphertext, signature)
        assert plaintext == b"Come va?"

    # Risposta di Gianni, letta da Mario e Luca
    ciphertext, signature = encrypt_group_message(gianni.sender_key, b"Tutto bene, e tu?")
    for receiver in (mario, luca):
        plaintext = decrypt_group_message(receiver.remote_sender_keys["Gianni"], ciphertext, signature)
        assert plaintext == b"Tutto bene, e tu?"

    # Firma manomessa: deve fallire senza corrompere la catena della vittima
    ciphertext, signature = encrypt_group_message(luca.sender_key, b"Messaggio di Luca")
    tampered_signature = bytes([signature[0] ^ 0xFF]) + signature[1:]
    with pytest.raises(InvalidSignature):
        decrypt_group_message(mario.remote_sender_keys["Luca"], ciphertext, tampered_signature)
