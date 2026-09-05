from app.core.rate_limiter import limiter


def test_login_rate_limit_blocks_after_threshold(client, make_user):
    # Azzera lo stato del limiter: senza, questo test dipenderebbe da quanti
    # tentativi di login sono già stati fatti da altri test nella stessa sessione
    # (slowapi tiene lo stato in memoria per tutta la durata del processo).
    limiter.reset()

    make_user("ratelimituser", "ratelimituser@test.com", "correctpass123")

    statuses = []
    for _ in range(6):
        response = client.post("/auth/login", json={
            "email": "ratelimituser@test.com",
            "password": "wrongpassword",
        })
        statuses.append(response.status_code)

    assert 429 in statuses
