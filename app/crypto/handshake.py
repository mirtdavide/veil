from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from app.schemas.key_bundle import KeyBundlePublish
from app.crypto.keys import IdentityKeys
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PublicKey
from app.schemas.key_bundle import KeyBundleResponse
import base64

def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def base64_to_bytes(data: str) -> bytes:
    return base64.b64decode(data)

def public_key_to_base64(public_key) -> str:
    raw_bytes = public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
    return bytes_to_base64(raw_bytes)

def public_key_from_base64(data: str, key_class):
    raw_bytes = base64_to_bytes(data)
    return key_class.from_public_bytes(raw_bytes)

def prepare_key_bundle(identity_keys: IdentityKeys) -> KeyBundlePublish:
    x25519_public_raw = identity_keys.x25519_public.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
    ml_kem_public_raw = identity_keys.ml_kem_public.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)

    x25519_signature = identity_keys.ed25519_private.sign(x25519_public_raw)
    ml_kem_signature = identity_keys.ml_dsa_private.sign(ml_kem_public_raw)

    return KeyBundlePublish(
        x25519_public=bytes_to_base64(x25519_public_raw),
        ml_kem_public=bytes_to_base64(ml_kem_public_raw),
        ed25519_public=public_key_to_base64(identity_keys.ed25519_public),
        ml_dsa_public=public_key_to_base64(identity_keys.ml_dsa_public),
        x25519_signature=bytes_to_base64(x25519_signature),
        ml_kem_signature=bytes_to_base64(ml_kem_signature),
    )

def verify_key_bundle(bundle: KeyBundleResponse) -> bool:
    ed25519_public = public_key_from_base64(bundle.ed25519_public, Ed25519PublicKey)
    ml_dsa_public = public_key_from_base64(bundle.ml_dsa_public, MLDSA65PublicKey)

    x25519_public_raw = base64_to_bytes(bundle.x25519_public)
    ml_kem_public_raw = base64_to_bytes(bundle.ml_kem_public)
    x25519_signature = base64_to_bytes(bundle.x25519_signature)
    ml_kem_signature = base64_to_bytes(bundle.ml_kem_signature)

    try:
        ed25519_public.verify(x25519_signature, x25519_public_raw)
        ml_dsa_public.verify(ml_kem_signature, ml_kem_public_raw)
    except InvalidSignature:
        return False
    return True

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def derive_shared_secret(segreto_dh: bytes, kem_secret: bytes) -> bytes:
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"veil-handshake")
    return hkdf.derive(segreto_dh + kem_secret)

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PublicKey

def initiate_handshake(my_identity_keys: IdentityKeys, peer_bundle: KeyBundleResponse) -> tuple[bytes, bytes]:
    peer_x25519_public = public_key_from_base64(peer_bundle.x25519_public, X25519PublicKey)
    peer_ml_kem_public = public_key_from_base64(peer_bundle.ml_kem_public, MLKEM768PublicKey)

    segreto_dh = my_identity_keys.x25519_private.exchange(peer_x25519_public)
    kem_secret, kem_ciphertext = peer_ml_kem_public.encapsulate()

    return derive_shared_secret(segreto_dh, kem_secret), kem_ciphertext


def respond_to_handshake(my_identity_keys: IdentityKeys, peer_x25519_public: X25519PublicKey, kem_ciphertext: bytes) -> bytes:
    segreto_dh = my_identity_keys.x25519_private.exchange(peer_x25519_public)
    kem_secret = my_identity_keys.ml_kem_private.decapsulate(kem_ciphertext)
    return derive_shared_secret(segreto_dh, kem_secret)