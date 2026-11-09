def test_account_lockout_after_five_failed_attempts(client):
    client.post("/register", json={
        "username": "lockuser",
        "password": "Correct@123"
    })

    for attempt in range(5):
        response = client.post("/login", json={
            "username": "lockuser",
            "password": "WrongPassword@123"
        })

    assert response.status_code == 429

    correct_login = client.post("/login", json={
        "username": "lockuser",
        "password": "Correct@123"
    })

    assert correct_login.status_code == 429