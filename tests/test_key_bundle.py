def test_publish_and_get_key_bundle(authenticated_client, make_user):
    user = make_user("keyuser", "keyuser@test.com")
    bundle_payload = {
        "x25519_public": "x25519pub",
        "ml_kem_public": "mlkempub",
        "ed25519_public": "ed25519pub",
        "ml_dsa_public": "mldsapub",
        "x25519_signature": "x25519sig",
        "ml_kem_signature": "mlkemsig",
    }

    publish_response = authenticated_client(user).post("/users/me/key-bundle", json=bundle_payload)
    assert publish_response.status_code == 200

    get_response = authenticated_client(user).get(f"/users/{user.id}/key-bundle")
    assert get_response.status_code == 200
    assert get_response.json()["x25519_public"] == "x25519pub"


def test_publish_key_bundle_twice_fails(authenticated_client, make_user):
    user = make_user("keyuser2", "keyuser2@test.com")
    bundle_payload = {
        "x25519_public": "a", "ml_kem_public": "b", "ed25519_public": "c",
        "ml_dsa_public": "d", "x25519_signature": "e", "ml_kem_signature": "f",
    }
    authenticated_client(user).post("/users/me/key-bundle", json=bundle_payload)

    response = authenticated_client(user).post("/users/me/key-bundle", json=bundle_payload)
    assert response.status_code == 400


def test_get_key_bundle_not_found(authenticated_client, make_user):
    user = make_user("keyuser3", "keyuser3@test.com")

    response = authenticated_client(user).get("/users/999999/key-bundle")
    assert response.status_code == 404
