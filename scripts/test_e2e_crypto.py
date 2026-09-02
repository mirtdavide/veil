"""
Collaudo end-to-end della crittografia E2E pairwise (Fase 6).

Non tocca il server: genera direttamente le chiavi di identita' di Mario e
Gianni in memoria e simula lo scambio di key bundle, per testare solo il
livello crittografico (handshake + Double Ratchet + orchestrazione) senza
dipendere da un'istanza FastAPI/PostgreSQL in esecuzione.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

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


async def main() -> None:
    print("Generazione chiavi di identita' per Mario e Gianni...")
    mario_keys = generate_identity_keys()
    gianni_keys = generate_identity_keys()

    mario_bundle = bundle_response_from_identity(1, mario_keys)
    gianni_bundle = bundle_response_from_identity(2, gianni_keys)

    associated_data = b"mario-gianni-conversation"

    print("\n[1] Mario manda il primo messaggio: 'Hey'")
    mario_ratchet, encoded_1 = await prepare_first_message(
        mario_keys, gianni_bundle, b"Hey", associated_data
    )
    gianni_ratchet, plaintext_1 = await receive_first_message(
        gianni_keys, mario_bundle, encoded_1, associated_data
    )
    print(f"    Gianni riceve: {plaintext_1.decode()!r}")
    assert plaintext_1 == b"Hey", "Primo messaggio non corrisponde!"

    print("\n[2] Mario manda un secondo messaggio (stesso turno): 'Come va?'")
    encoded_2 = await prepare_message(mario_ratchet, b"Come va?", associated_data)
    plaintext_2 = await receive_message_from_string(gianni_ratchet, encoded_2, associated_data)
    print(f"    Gianni riceve: {plaintext_2.decode()!r}")
    assert plaintext_2 == b"Come va?", "Secondo messaggio non corrisponde!"

    print("\n[3] Gianni risponde (cambio di turno): 'Tutto bene!'")
    encoded_3 = await prepare_message(gianni_ratchet, b"Tutto bene!", associated_data)
    plaintext_3 = await receive_message_from_string(mario_ratchet, encoded_3, associated_data)
    print(f"    Mario riceve: {plaintext_3.decode()!r}")
    assert plaintext_3 == b"Tutto bene!", "Messaggio di risposta non corrisponde!"

    print("\n[4] Mario risponde di nuovo (secondo cambio di turno): 'Bene, tu?'")
    encoded_4 = await prepare_message(mario_ratchet, b"Bene, tu?", associated_data)
    plaintext_4 = await receive_message_from_string(gianni_ratchet, encoded_4, associated_data)
    print(f"    Gianni riceve: {plaintext_4.decode()!r}")
    assert plaintext_4 == b"Bene, tu?", "Quarto messaggio non corrisponde!"

    print("\nTutti i controlli superati: handshake + Double Ratchet pairwise funzionano end-to-end,")
    print("inclusi i cambi di turno in entrambe le direzioni.")


if __name__ == "__main__":
    asyncio.run(main())
