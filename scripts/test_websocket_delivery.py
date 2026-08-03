import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json

import httpx
import websockets

from app.core.database import SessionLocal
from app.models.message import Message
from app.models.message_status import MessageStatus

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"


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


def get_delivered_at(message_id: int, user_id: int):
    db = SessionLocal()
    try:
        status = db.query(MessageStatus).filter(
            MessageStatus.message_id == message_id,
            MessageStatus.user_id == user_id,
        ).first()
        return status.delivered_at if status else "NO STATUS ROW"
    finally:
        db.close()


def report(label: str, ok: bool, detail):
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {label}: {detail}")


def get_read_at(message_id: int, user_id: int):
    db = SessionLocal()
    try:
        status = db.query(MessageStatus).filter(
            MessageStatus.message_id == message_id,
            MessageStatus.user_id == user_id,
        ).first()
        return status.read_at if status else "NO STATUS ROW (probabilmente ripulita da mark_all_read)"
    finally:
        db.close()


def get_all_read_flag(message_id: int):
    db = SessionLocal()
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        return message.all_read if message else "MESSAGE NOT FOUND"
    finally:
        db.close()


def count_status_rows(message_id: int) -> int:
    db = SessionLocal()
    try:
        return db.query(MessageStatus).filter(MessageStatus.message_id == message_id).count()
    finally:
        db.close()


async def main():
    if len(sys.argv) != 5:
        print("Usage: python scripts/test_websocket_delivery.py <email_a> <password_a> <email_b> <password_b>")
        sys.exit(1)

    email_a, password_a, email_b, password_b = sys.argv[1:5]

    async with httpx.AsyncClient() as client:
        token_a = await login(client, email_a, password_a)
        token_b = await login(client, email_b, password_b)
        user_a_id = await get_user_id(client, token_a)
        user_b_id = await get_user_id(client, token_b)
        conversation_id = await get_or_create_direct_conversation(client, token_a, user_b_id)

    print(f"User A id={user_a_id} | User B id={user_b_id} | conversation id={conversation_id}\n")

    # --- TEST A: entrambi online -> consegna via push in tempo reale ---
    print("=== TEST A: push in tempo reale (B online) ===")
    async with websockets.connect(f"{WS_URL}?token={token_a}") as ws_a, \
               websockets.connect(f"{WS_URL}?token={token_b}") as ws_b:

        await ws_a.send(json.dumps({
            "conversation_id": conversation_id,
            "content_encrypted": "test A: push delivery",
            "type": "text",
        }))

        confirm = json.loads(await asyncio.wait_for(ws_a.recv(), timeout=5))
        message_id = confirm["id"]
        print(f"A riceve conferma, message id={message_id}")

        pushed = json.loads(await asyncio.wait_for(ws_b.recv(), timeout=5))
        report("B riceve il push in tempo reale", pushed["id"] == message_id, pushed)

        await asyncio.sleep(0.3)  # lascia il tempo al commit di mark_delivered

    delivered = get_delivered_at(message_id, user_b_id)
    report("delivered_at per B dopo il push", delivered not in (None, "NO STATUS ROW"), delivered)

    # --- TEST B: B offline al momento dell'invio, poi si riconnette ---
    print("\n=== TEST B: B offline, poi si riconnette (mark_all_delivered) ===")
    async with websockets.connect(f"{WS_URL}?token={token_a}") as ws_a:
        await ws_a.send(json.dumps({
            "conversation_id": conversation_id,
            "content_encrypted": "test B: B era offline",
            "type": "text",
        }))
        message_id_2 = json.loads(await asyncio.wait_for(ws_a.recv(), timeout=5))["id"]

    await asyncio.sleep(0.3)
    delivered_before = get_delivered_at(message_id_2, user_b_id)
    report("delivered_at per B PRIMA della riconnessione (atteso None)", delivered_before is None, delivered_before)

    async with websockets.connect(f"{WS_URL}?token={token_b}") as ws_b:
        await asyncio.sleep(0.3)  # lascia il tempo a mark_all_delivered

    delivered_after = get_delivered_at(message_id_2, user_b_id)
    report("delivered_at per B DOPO la riconnessione", delivered_after not in (None, "NO STATUS ROW"), delivered_after)

    # --- TEST C: B dichiara "letto fino a qui" -> read_at + all_read + cleanup + push al mittente ---
    print("\n=== TEST C: spunta blu (mark_read + all_read + cleanup + push in tempo reale) ===")
    async with websockets.connect(f"{WS_URL}?token={token_a}") as ws_a:
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                f"{BASE_URL}/conversations/{conversation_id}/read",
                json={"up_to_message_id": message_id_2},
                headers={"Authorization": f"Bearer {token_b}"},
            )
            resp.raise_for_status()
            newly_all_read = resp.json()
            print(f"Endpoint /read risponde: {newly_all_read}")

        read_push = json.loads(await asyncio.wait_for(ws_a.recv(), timeout=5))
        print(f"A (mittente) riceve sul WS: {read_push}")
        report(
            "il push contiene l'evento messages_read con l'id giusto",
            read_push.get("event") == "messages_read" and message_id_2 in read_push.get("message_ids", []),
            read_push,
        )

    report(
        "il messaggio 2 risulta tra i 'newly all read'",
        message_id_2 in newly_all_read,
        newly_all_read,
    )

    all_read_flag = get_all_read_flag(message_id_2)
    report("Message.all_read è True", all_read_flag is True, all_read_flag)

    remaining_rows = count_status_rows(message_id_2)
    report("le righe MessageStatus di quel messaggio sono state ripulite (atteso 0)", remaining_rows == 0, remaining_rows)

    read_at_after_cleanup = get_read_at(message_id_2, user_b_id)
    print(f"(informativo) query diretta sulla riga status ormai cancellata: {read_at_after_cleanup}")


if __name__ == "__main__":
    asyncio.run(main())
