"""
Collaudo end-to-end dei Sender Keys per i gruppi (Fase 6).

Simula un gruppo con 3 persone (Mario, Gianni, Luca): ognuno crea la
propria Sender Key e la distribuisce agli altri due attraverso un Double
Ratchet pairwise creato al volo in questo stesso script (nessun server
coinvolto, stesso approccio di test_e2e_crypto.py), poi verifica che i
messaggi di gruppo cifrati da uno vengano decifrati correttamente dagli
altri due, e che una firma manomessa venga rifiutata.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

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
    """Stato locale (client-side, simulato) di un membro del gruppo."""

    def __init__(self, name: str, user_id: int):
        self.name = name
        self.user_id = user_id
        self.identity_keys = generate_identity_keys()
        self.bundle: KeyBundleResponse | None = None
        self.sender_key = generate_sender_key()
        self.pairwise_ratchets: dict[str, object] = {}
        self.remote_sender_keys: dict[str, object] = {}


async def exchange_sender_keys(a: Member, b: Member, associated_data: bytes) -> None:
    """A e B si scambiano le rispettive Sender Key attraverso un Double Ratchet pairwise nuovo."""

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


async def main() -> None:
    print("Creazione dei 3 membri del gruppo: Mario, Gianni, Luca...")
    mario = Member("Mario", 1)
    gianni = Member("Gianni", 2)
    luca = Member("Luca", 3)
    members = [mario, gianni, luca]

    for member in members:
        member.bundle = bundle_response_from_identity(member.user_id, member.identity_keys)

    associated_data = b"gruppo-mario-gianni-luca"

    print("\nSetup: ogni coppia si scambia la propria Sender Key via Double Ratchet pairwise...")
    await exchange_sender_keys(mario, gianni, associated_data)
    await exchange_sender_keys(mario, luca, associated_data)
    await exchange_sender_keys(gianni, luca, associated_data)
    print("Setup completato: ognuno ha la Sender Key remota degli altri due.")

    print("\n[1] Mario scrive nel gruppo: 'Ciao a tutti citrulli'")
    ciphertext, signature = encrypt_group_message(mario.sender_key, b"Ciao a tutti citrulli")
    for receiver in (gianni, luca):
        plaintext = decrypt_group_message(receiver.remote_sender_keys["Mario"], ciphertext, signature)
        print(f"    {receiver.name} riceve: {plaintext.decode()!r}")
        assert plaintext == b"Ciao a tutti citrulli", f"{receiver.name} ha decifrato male il messaggio di Mario!"

    print("\n[2] Mario scrive un secondo messaggio: 'Come va?'")
    ciphertext, signature = encrypt_group_message(mario.sender_key, b"Come va?")
    for receiver in (gianni, luca):
        plaintext = decrypt_group_message(receiver.remote_sender_keys["Mario"], ciphertext, signature)
        print(f"    {receiver.name} riceve: {plaintext.decode()!r}")
        assert plaintext == b"Come va?", f"{receiver.name} ha decifrato male il secondo messaggio di Mario!"

    print("\n[3] Gianni risponde nel gruppo: 'Tutto bene, e tu?'")
    ciphertext, signature = encrypt_group_message(gianni.sender_key, b"Tutto bene, e tu?")
    for receiver in (mario, luca):
        plaintext = decrypt_group_message(receiver.remote_sender_keys["Gianni"], ciphertext, signature)
        print(f"    {receiver.name} riceve: {plaintext.decode()!r}")
        assert plaintext == b"Tutto bene, e tu?", f"{receiver.name} ha decifrato male il messaggio di Gianni!"

    print("\n[4] Verifica di sicurezza: una firma manomessa deve far fallire la decifratura")
    ciphertext, signature = encrypt_group_message(luca.sender_key, b"Messaggio di Luca")
    tampered_signature = bytes([signature[0] ^ 0xFF]) + signature[1:]
    try:
        decrypt_group_message(mario.remote_sender_keys["Luca"], ciphertext, tampered_signature)
        raise AssertionError("La firma manomessa avrebbe dovuto far fallire la verifica!")
    except InvalidSignature:
        print("    Rifiutato correttamente: InvalidSignature")

    print("\nTutti i controlli superati: Sender Keys per i gruppi funzionano end-to-end,")
    print("incluso il rifiuto di un messaggio con firma manomessa.")


if __name__ == "__main__":
    asyncio.run(main())
