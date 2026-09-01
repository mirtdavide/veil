from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PrivateKey, MLKEM768PublicKey
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey, MLDSA65PublicKey


@dataclass
class IdentityKeys:
    x25519_private: X25519PrivateKey
    x25519_public: X25519PublicKey
    ml_kem_private: MLKEM768PrivateKey
    ml_kem_public: MLKEM768PublicKey
    ed25519_private: Ed25519PrivateKey
    ed25519_public: Ed25519PublicKey
    ml_dsa_private: MLDSA65PrivateKey
    ml_dsa_public: MLDSA65PublicKey




def generate_x25519_keypair() -> tuple[X25519PrivateKey, X25519PublicKey]:
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

def generate_ml_kem_keypair() -> tuple[MLKEM768PrivateKey, MLKEM768PublicKey]:
    private_key = MLKEM768PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def generate_ed25519_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def generate_ml_dsa_keypair() -> tuple[MLDSA65PrivateKey, MLDSA65PublicKey]:
    private_key = MLDSA65PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

def generate_identity_keys() -> IdentityKeys:
    x25519_private, x25519_public = generate_x25519_keypair()
    ml_kem_private, ml_kem_public = generate_ml_kem_keypair()
    ed25519_private, ed25519_public = generate_ed25519_keypair()
    ml_dsa_private, ml_dsa_public = generate_ml_dsa_keypair()

    return IdentityKeys(
        x25519_private=x25519_private,
        x25519_public=x25519_public,
        ml_kem_private=ml_kem_private,
        ml_kem_public=ml_kem_public,
        ed25519_private=ed25519_private,
        ed25519_public=ed25519_public,
        ml_dsa_private=ml_dsa_private,
        ml_dsa_public=ml_dsa_public
    )