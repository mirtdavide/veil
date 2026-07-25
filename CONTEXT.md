# Veil — Contesto di Sviluppo

## Cos'è Veil

App di messaggistica E2E cifrata per uso personale (~50 utenti tra amici e parenti). Clone di WhatsApp con crittografia post-quantum ibrida. Registrazione su invito con codice univoco monouso.

---

## Stack

| Componente | Scelta |
|---|---|
| Backend | FastAPI + PostgreSQL + SQLAlchemy |
| Real-time | WebSocket |
| Auth | JWT access token (30min) + refresh token (7 giorni) |
| Crittografia | X25519 + ML-KEM-768, AES-256-GCM, Ed25519 + ML-DSA-65 (ibrido post-quantum) |
| Registrazione | Invite code univoco, monouso, con scadenza |
| Storage testo | Persistente |
| Storage media | Relay temporaneo — cancellato dopo consegna |
| Infrastruttura | Oracle Free Tier, singolo nodo Ampere ARM |
| Client | Web prima, mobile dopo |

---

## Struttura progetto

```
veil/
├── app/
│   ├── main.py               # Entry point FastAPI
│   ├── config.py             # Pydantic-settings (.env)
│   ├── dependencies.py       # get_db(), get_auth_service()
│   ├── routers/
│   │   └── auth.py           # POST /auth/register, POST /auth/login ✅
│   ├── services/
│   │   └── auth_service.py   # register(), login() ✅
│   ├── repositories/
│   │   ├── user_repository.py
│   │   └── invite_code_repositories.py
│   ├── models/
│   │   ├── user.py
│   │   ├── invite_code.py
│   │   ├── conversation.py
│   │   ├── conversation_member.py
│   │   ├── message.py
│   │   ├── message_status.py
│   │   └── media_file.py
│   ├── schemas/
│   │   ├── auth.py           # UserRegister, UserLogin, UserResponse
│   │   ├── message.py        # MessageSend, MessageResponse
│   │   ├── conversation.py   # ConversationCreate, ConversationResponse
│   │   └── invite_code.py    # InviteCodeCreate, InviteCodeResponse
│   └── core/
│       ├── database.py       # engine, SessionLocal, Base
│       └── security.py       # hash_password, verify_password, JWT
├── scripts/
│   ├── create_admin.py       # CLI: crea primo utente admin
│   └── create_invite.py      # CLI: genera invite code
├── alembic/                  # Migrations
├── docs/                     # Note di sviluppo e documentazione
├── .env                      # NON committare
├── .env.example
└── pyproject.toml
```

---

## Pattern architetturale

**Router → Service → Repository**

| Layer | Responsabilità | Sa di HTTP? | Sa del DB? |
|---|---|---|---|
| Router | Riceve request, valida input, chiama service | ✅ | ❌ |
| Service | Business logic, regole, orchestrazione | ❌ | ❌ |
| Repository | Query al database | ❌ | ✅ |

---

## Modelli ORM

### User
- `id`, `username` (unique), `email` (unique), `hashed_password`
- `public_key` (nullable — popolato quando implementiamo crypto)
- `avatar_path` (nullable), `bio` (nullable)
- `is_active` (default True), `can_invite` (default False)
- `created_at` (server_default)

### InviteCode
- `id`, `code` (unique), `created_by` (FK users.id)
- `created_at` (server_default), `expires_at`, `used_at` (nullable)

### Conversation
- `id`, `type` (direct/group), `name` (nullable, solo gruppi)
- `created_by` (FK users.id), `created_at`

### ConversationMember
- `id`, `conversation_id` (FK), `user_id` (FK), `joined_at`

### Message
- `id`, `conversation_id` (FK), `sender_id` (FK)
- `content_encrypted` (Text), `type` (text/image/audio/video/sticker)
- `all_read` (bool, default False — ottimizzazione spunte), `created_at`

### MessageStatus
- `id`, `message_id` (FK), `user_id` (FK)
- `delivered_at` (nullable), `read_at` (nullable)

### MediaFile
- `id`, `message_id` (FK), `file_type`, `file_path`
- `delivered_at` (nullable — None finché non scaricato, poi cancellato)

---

## Decisioni architetturali importanti

- **Invite-only:** primo utente creato via CLI (`scripts/create_admin.py`), poi genera invite codes con `scripts/create_invite.py`
- **`can_invite`** su User: non tutti possono invitare, default False. L'admin lo abilita manualmente
- **`all_read`** su Message: quando tutti i `MessageStatus` hanno `read_at`, si setta `all_read=True` e si cancellano i record di status per risparmiare storage
- **Media relay temporaneo:** `delivered_at` su `MediaFile` è None finché il destinatario non scarica. Dopo la consegna il file viene cancellato
- **`public_key` nullable:** campo per crittografia E2E, popolato nella Fase 6. Per ora None
- **Spunte blu nei gruppi:** `MessageStatus` ha una riga per ogni membro. Spunta blu = tutti i membri hanno `read_at` non None
- **Timezone:** PostgreSQL salva datetime senza timezone. Fix: `datetime_field.replace(tzinfo=timezone.utc)` prima dei confronti

---

## Fasi completate

### ✅ Fase 1 — Setup
`uv`, struttura cartelle, FastAPI base, `pydantic-settings`, `.env`

### ✅ Fase 2 — Database e modelli
PostgreSQL, SQLAlchemy engine/session, 7 modelli ORM, Alembic configurato e migrations applicate

### ✅ Fase 3 — Schemas Pydantic
`UserRegister`, `UserLogin`, `UserResponse`, `MessageSend`, `MessageResponse`, `ConversationCreate`, `ConversationResponse`, `InviteCodeCreate`, `InviteCodeResponse`

### ✅ Fase 4 — Autenticazione
Bcrypt, JWT (access + refresh), `UserRepository`, `InviteCodeRepository`, `AuthService`, router `/auth/register` e `/auth/login`, dependency injection con `Depends`, script CLI admin e invite

---

## Prossima fase

### 👉 Fase 5 — Messaggistica
- WebSocket: cos'è, differenza con HTTP, quando si usa
- Repository e service layer per `Conversation` e `Message`
- Endpoint REST: creare conversazione, recuperare storia messaggi
- WebSocket per messaggi in tempo reale
- Gestione `MessageStatus` (spunte)
- Relay media: upload, consegna, cancellazione automatica

---

## Fasi rimanenti

| Fase | Contenuto |
|---|---|
| 6 | Crittografia E2E post-quantum (liboqs-python, X25519+ML-KEM-768, AES-256-GCM) |
| 7 | Qualità e sicurezza (rate limiting, CORS, security headers, logging) |
| 8 | Testing (pytest da zero, unit test, integration test) |
| 9 | Deployment (Docker, Oracle Free Tier, HTTPS) |
| 10 | Frontend (SPA HTML/CSS/JS, revisione sicurezza prima dell'uso reale) |

---

## Dipendenze installate

```toml
dependencies = [
    "fastapi[standard]",
    "sqlalchemy",
    "alembic",
    "pydantic-settings",
    "python-jose[cryptography]",
    "passlib[bcrypt]",
    "bcrypt==4.0.1",      # versione specifica per compatibilità con passlib
    "cryptography",
    "psycopg2-binary",
]
```

---

## Errori comuni e fix

| Errore | Causa | Fix |
|---|---|---|
| `passlib` + `bcrypt` incompatibili | versioni recenti bcrypt cambiano API interna | `uv add "bcrypt==4.0.1"` |
| `can't compare offset-naive and offset-aware datetimes` | PostgreSQL salva senza timezone | `.replace(tzinfo=timezone.utc)` prima del confronto |
| `NoReferencedTableError` negli script CLI | modelli con FK non importati | importare tutti i modelli collegati nello script |
| `InsufficientPrivilege schema public` | PostgreSQL 15+ cambia default permessi | `GRANT ALL ON SCHEMA public TO veil_user;` in pgAdmin |
| `extra_forbidden` in pydantic-settings | variabili ENV non mappate | aggiungere `extra="ignore"` a `SettingsConfigDict` |
