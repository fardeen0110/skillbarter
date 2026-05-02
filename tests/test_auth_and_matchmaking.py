def register_user(client, *, name="Alex Jordan", email="alex@example.com", password="password123"):
    response = client.post(
        "/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )
    return response


def login_user(client, *, email="alex@example.com", password="password123"):
    response = client.post(
        "/login",
        json={
            "email": email,
            "password": password,
        },
    )
    return response


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_creates_user(client):
    response = register_user(client)

    assert response.status_code == 201
    payload = response.json()

    assert payload["message"] == "Account created successfully"
    assert payload["user"]["name"] == "Alex Jordan"
    assert payload["user"]["email"] == "alex@example.com"
    assert "id" in payload["user"]
    assert "created_at" in payload["user"]


def test_login_returns_access_token_and_user(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200
    payload = response.json()

    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] > 0
    assert isinstance(payload["access_token"], str)
    assert payload["user"]["email"] == "alex@example.com"


def test_me_returns_authenticated_user(client):
    register_user(client)
    login_response = login_user(client)
    token = login_response.json()["access_token"]

    response = client.get("/me", headers=auth_headers(token))

    assert response.status_code == 200
    payload = response.json()

    assert payload["name"] == "Alex Jordan"
    assert payload["email"] == "alex@example.com"


def test_matchmaking_returns_top_five_matches(client):
    register_user(client)
    login_response = login_user(client)
    token = login_response.json()["access_token"]

    response = client.post(
        "/matchmaking",
        headers=auth_headers(token),
        json={
            "skill_offer": "React",
            "skill_want": "Product Strategy",
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert "matches" in payload
    assert len(payload["matches"]) == 5
    assert all("name" in match for match in payload["matches"])
    assert all("skill" in match for match in payload["matches"])
    assert all(0 <= match["score"] <= 100 for match in payload["matches"])


def test_matchmaking_requires_authentication(client):
    response = client.post(
        "/matchmaking",
        json={
            "skill_offer": "React",
            "skill_want": "Product Strategy",
        },
    )

    assert response.status_code == 401
