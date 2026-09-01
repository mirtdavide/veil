import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

import httpx

from app.config import settings
from app.core.database import SessionLocal
from app.models.media_file import MediaFile
from app.models.media_file_status import MediaFileStatus

BASE_URL = "http://127.0.0.1:8000"

TEST_FILENAME = "test.png"
TEST_FILE_CONTENT = b"fake png content used for automated media relay test"


async def login(client: httpx.AsyncClient, email: str, password: str) -> str:
    resp = await client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    resp.raise_for_status()
    return resp.json()["access_token"]


async def get_user_id(client: httpx.AsyncClient, token: str) -> int:
    resp = await client.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    return resp.json()["id"]


async def get_or_create_direct_conversation(client: httpx.AsyncClient, token: str, other_user_id: int) -> int:
    resp = await client.post(
        f"{BASE_URL}/conversations",
        json={"type": "direct", "name": None, "member_ids": [other_user_id]},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    return resp.json()["id"]


def get_media_file_disk_path(media_file_id: int) -> str | None:
    db = SessionLocal()
    try:
        media_file = db.query(MediaFile).filter(MediaFile.id == media_file_id).first()
        if media_file is None:
            return None
        return os.path.join(settings.media_storage_path, media_file.file_path)
    finally:
        db.close()


def media_file_row_exists(media_file_id: int) -> bool:
    db = SessionLocal()
    try:
        return db.query(MediaFile).filter(MediaFile.id == media_file_id).first() is not None
    finally:
        db.close()


def count_status_rows(media_file_id: int) -> int:
    db = SessionLocal()
    try:
        return db.query(MediaFileStatus).filter(MediaFileStatus.media_file_id == media_file_id).count()
    finally:
        db.close()


def report(label: str, ok: bool, detail):
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {label}: {detail}")


async def main():
    if len(sys.argv) != 5:
        print("Usage: python scripts/test_media_relay.py <email_a> <password_a> <email_b> <password_b>")
        sys.exit(1)

    email_a, password_a, email_b, password_b = sys.argv[1:5]

    async with httpx.AsyncClient() as client:
        token_a = await login(client, email_a, password_a)
        token_b = await login(client, email_b, password_b)
        user_a_id = await get_user_id(client, token_a)
        user_b_id = await get_user_id(client, token_b)
        conversation_id = await get_or_create_direct_conversation(client, token_a, user_b_id)

        print(f"User A (uploader) id={user_a_id} | User B (downloader) id={user_b_id} | conversation id={conversation_id}\n")

        # --- TEST A: upload ---
        print("=== TEST A: upload ===")
        files = {"file": (TEST_FILENAME, TEST_FILE_CONTENT, "image/png")}
        data = {"caption": "test media relay", "media_type": "image"}
        resp = await client.post(
            f"{BASE_URL}/conversations/{conversation_id}/media",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {token_a}"},
        )
        resp.raise_for_status()
        body = resp.json()
        media_file_id = body["id"]
        print(f"Upload risponde: {body}")
        report(
            "response contiene id/message_id/file_type",
            all(k in body for k in ("id", "message_id", "file_type")),
            body,
        )

        disk_path = get_media_file_disk_path(media_file_id)
        report("il file esiste su disco dopo l'upload", disk_path is not None and os.path.exists(disk_path), disk_path)

        with open(disk_path, "rb") as f:
            on_disk_content = f.read()
        report(
            "il contenuto su disco corrisponde a quello caricato",
            on_disk_content == TEST_FILE_CONTENT,
            f"{len(on_disk_content)} bytes",
        )

        report(
            "esiste una riga MediaFileStatus per B, non ancora scaricata",
            count_status_rows(media_file_id) == 1,
            count_status_rows(media_file_id),
        )

        # --- TEST B: download da parte dell'unico altro membro -> cleanup atteso ---
        print("\n=== TEST B: download (destinatario unico -> cleanup atteso) ===")
        resp_download = await client.get(
            f"{BASE_URL}/media/{media_file_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        resp_download.raise_for_status()

        # la cancellazione file+DB gira in un BackgroundTask, DOPO che la risposta e' stata
        # inviata al client: diamogli un attimo per finire prima di controllare lo stato
        await asyncio.sleep(0.5)

        report(
            "il download restituisce lo stesso contenuto caricato",
            resp_download.content == TEST_FILE_CONTENT,
            f"{len(resp_download.content)} bytes",
        )

        report("il file è stato cancellato dal disco dopo l'unico download", not os.path.exists(disk_path), disk_path)
        report("la riga MediaFile è stata cancellata dal DB", not media_file_row_exists(media_file_id), media_file_id)
        report(
            "le righe MediaFileStatus sono state ripulite",
            count_status_rows(media_file_id) == 0,
            count_status_rows(media_file_id),
        )

        # --- TEST C: negativo - riscaricare un file già consumato ---
        print("\n=== TEST C: secondo tentativo di download -> 404 atteso ===")
        resp_second = await client.get(
            f"{BASE_URL}/media/{media_file_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        report("il secondo download restituisce 404 (file già consumato)", resp_second.status_code == 404, resp_second.status_code)


if __name__ == "__main__":
    asyncio.run(main())
