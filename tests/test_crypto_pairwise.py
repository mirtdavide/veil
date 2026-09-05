"""
Versione pytest di scripts/test_e2e_crypto.py — stessa logica, adattata al
framework di test invece che a uno script lanciato a mano.
"""
import pytest

from app.crypto.keys import generate_identity_keys
from app.crypto.handshake import prepare_key_bundle
from app.schemas.key_bundle import KeyBundleResponse
from app.crypto.conversation import (
    prepare_first_message,
    receive_first_message,
    prepare_message,
    receive_message_from_string,
)


def bundle_response_from_identity(user_id: int, identity_keys) -> KeyBundleResponse:
    publish = prepare_key_bundle(identity_keys)
    return KeyBundleResponse(user_id=user_id, **publish.model_dump())


@pytest.mark.asyncio
async def test_pairwise_double_ratchet_end_to_end():
    mario_keys = generate_identity_keys()
    gianni_keys = generate_identity_keys()

    mario_bundle = bundle_response_from_identity(1, mario_keys)
    gianni_bundle = bundle_response_from_identity(2, gianni_keys)

    associated_data = b"mario-gianni-conversation"

    # Primo messaggio: handshake completo
    mario_ratchet, encoded_1 = await prepare_first_message(mario_keys, gianni_bundle, b"Hey", associated_data)
    gianni_ratchet, plaintext_1 = await receive_first_message(gianni_keys, mario_bundle, encoded_1, associated_data)
    assert plaintext_1 == b"Hey"

    # Secondo messaggio, stesso turno
    encoded_2 = await prepare_message(mario_ratchet, b"Come va?", associated_data)
    plaintext_2 = await receive_message_from_string(gianni_ratchet, encoded_2, associated_data)
    assert plaintext_2 == b"Come va?"

    # Cambio di turno: risponde Gianni
    encoded_3 = await prepare_message(gianni_ratchet, b"Tutto bene!", associated_data)
    plaintext_3 = await receive_message_from_string(mario_ratchet, encoded_3, associated_data)
    assert plaintext_3 == b"Tutto bene!"

    # Secondo cambio di turno, di nuovo verso Mario
    encoded_4 = await prepare_message(mario_ratchet, b"Bene, tu?", associated_data)
    plaintext_4 = await receive_message_from_string(gianni_ratchet, encoded_4, associated_data)
    assert plaintext_4 == b"Bene, tu?"
