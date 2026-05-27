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


def update_profile(client, token, **overrides):
    payload = {
        "name": "Alex Jordan",
        "bio": "Product-minded builder",
        "city": "Bengaluru",
        "availability": "weeknights, saturdays",
        "experience_level": "advanced",
        "linkedin": "",
        "website": "",
        "x": "",
        "skills_offered": ["React", "Product Strategy"],
        "skills_wanted": ["Growth Marketing", "Python"],
    }
    payload.update(overrides)
    return client.patch("/profile", json=payload, headers=auth_headers(token))


def test_register_creates_user(client):
    response = register_user(client)

    assert response.status_code == 201
    payload = response.json()

    assert payload["message"].startswith("Account created successfully")
    assert payload["user"]["name"] == "Alex Jordan"
    assert payload["user"]["email"] == "alex@example.com"
    assert "id" in payload["user"]
    assert "created_at" in payload["user"]
    assert payload["user"]["profile"]["skills_offered"] == []


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
    update_profile(client, token)

    for index in range(5):
      name = f"Member {index}"
      email = f"member{index}@example.com"
      register_user(client, name=name, email=email)
      peer_token = login_user(client, email=email).json()["access_token"]
      update_profile(
          client,
          peer_token,
          name=name,
          bio="Peer profile",
          city="Mumbai",
          availability="weeknights, saturdays",
          experience_level="advanced",
          skills_offered=["Product Strategy", "Growth Marketing", "Python"] if index % 2 == 0 else ["Python", "Figma"],
          skills_wanted=["React", "Public Speaking"],
      )

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
    assert len(payload["matches"]) >= 1
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
