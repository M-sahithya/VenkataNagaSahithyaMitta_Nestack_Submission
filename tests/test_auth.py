def test_registration(client):
    response = client.post("/register", json={
        "username": "newuser",
        "password": "Password@123"
    })

    assert response.status_code == 201


def test_duplicate_registration(client):
    data = {
        "username": "newuser",
        "password": "Password@123"
    }

    client.post("/register", json=data)

    response = client.post("/register", json=data)

    assert response.status_code == 409


def test_successful_login(client):
    client.post("/register", json={
        "username": "loginuser",
        "password": "Password@123"
    })

    response = client.post("/login", json={
        "username": "loginuser",
        "password": "Password@123"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_invalid_login(client):
    response = client.post("/login", json={
        "username": "unknown",
        "password": "WrongPassword@123"
    })

    assert response.status_code == 401


def test_role_injection_blocked(client):
    response = client.post("/register", json={
        "username": "attacker",
        "password": "Password@123",
        "role": "admin"
    })

    assert response.status_code == 400