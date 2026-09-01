from pydantic import BaseModel


class KeyBundlePublish(BaseModel):
    x25519_public: str
    ml_kem_public: str
    ed25519_public: str
    ml_dsa_public: str
    x25519_signature: str
    ml_kem_signature: str


class KeyBundleResponse(BaseModel):
    user_id: int
    x25519_public: str
    ml_kem_public: str
    ed25519_public: str
    ml_dsa_public: str
    x25519_signature: str
    ml_kem_signature: str