import io


def test_upload_and_download_media(authenticated_client, make_user):
    alice = make_user("alice8", "alice8@test.com")
    bob = make_user("bob8", "bob8@test.com")

    conv = authenticated_client(alice).post("/conversations", json={
        "type": "direct", "name": None, "member_ids": [bob.id],
    }).json()

    fake_image = io.BytesIO(b"fake image bytes")
    upload_response = authenticated_client(alice).post(
        f"/conversations/{conv['id']}/media",
        files={"file": ("photo.jpg", fake_image, "image/jpeg")},
        data={"caption": "una foto", "media_type": "image"},
    )
    assert upload_response.status_code == 200
    media_id = upload_response.json()["id"]

    download_response = authenticated_client(bob).get(f"/media/{media_id}")
    assert download_response.status_code == 200


def test_upload_media_with_invalid_extension(authenticated_client, make_user):
    alice = make_user("alice9", "alice9@test.com")
    bob = make_user("bob9", "bob9@test.com")

    conv = authenticated_client(alice).post("/conversations", json={
        "type": "direct", "name": None, "member_ids": [bob.id],
    }).json()

    fake_file = io.BytesIO(b"not really an image")
    response = authenticated_client(alice).post(
        f"/conversations/{conv['id']}/media",
        files={"file": ("virus.exe", fake_file, "application/octet-stream")},
        data={"caption": "", "media_type": "image"},
    )
    assert response.status_code == 400


def test_non_member_cannot_upload_media(authenticated_client, make_user):
    alice = make_user("alice10", "alice10@test.com")
    bob = make_user("bob10", "bob10@test.com")
    stranger = make_user("stranger10", "stranger10@test.com")

    conv = authenticated_client(alice).post("/conversations", json={
        "type": "direct", "name": None, "member_ids": [bob.id],
    }).json()

    fake_image = io.BytesIO(b"fake image bytes")
    response = authenticated_client(stranger).post(
        f"/conversations/{conv['id']}/media",
        files={"file": ("photo.jpg", fake_image, "image/jpeg")},
        data={"caption": "", "media_type": "image"},
    )
    assert response.status_code == 404
