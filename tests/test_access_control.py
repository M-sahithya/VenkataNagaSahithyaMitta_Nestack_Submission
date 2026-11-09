
def test_unauthenticated_access(client):
    response = client.get("/records/1")
    assert response.status_code == 401


def test_user_can_access_own_record(client, user_a):
    headers = {"Authorization": f"Bearer {user_a}"}

    created = client.post(
        "/records",
        json={
            "title": "Private Record",
            "body": "User A private data"
        },
        headers=headers
    )

    assert created.status_code == 201

    record_id = created.json()["record"]["id"]

    response = client.get(
        f"/records/{record_id}",
        headers=headers
    )

    assert response.status_code == 200


def test_user_cannot_access_another_users_record(
    client, user_a, user_b
):
    headers_a = {"Authorization": f"Bearer {user_a}"}
    headers_b = {"Authorization": f"Bearer {user_b}"}

    created = client.post(
        "/records",
        json={
            "title": "User A Secret",
            "body": "Confidential information"
        },
        headers=headers_a
    )

    assert created.status_code == 201

    record_id = created.json()["record"]["id"]

    response = client.get(
        f"/records/{record_id}",
        headers=headers_b
    )

    assert response.status_code == 404


def test_admin_can_access_another_users_record(client, db, user_a):
    from app.models import User
    from app.security.passwords import hash_password

    # Create admin directly in the test database
    admin = User(
        username="testadmin",
        password_hash=hash_password("AdminPassword@123"),
        role="admin",
        failed_login_attempts=0
    )

    db.add(admin)
    db.commit()

    # User A creates a private record
    user_headers = {
        "Authorization": f"Bearer {user_a}"
    }

    created = client.post(
        "/records",
        json={
            "title": "User A Private Record",
            "body": "This belongs to User A."
        },
        headers=user_headers
    )

    assert created.status_code == 201

    record_id = created.json()["record"]["id"]

    # Admin logs in
    login = client.post(
        "/login",
        json={
            "username": "testadmin",
            "password": "AdminPassword@123"
        }
    )

    assert login.status_code == 200

    admin_token = login.json()["access_token"]

    admin_headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    # Admin accesses User A's record
    response = client.get(
        f"/records/{record_id}",
        headers=admin_headers
    )

    assert response.status_code == 200

def test_logout_revokes_session(client, user_a):
    headers = {
        "Authorization": f"Bearer {user_a}"
    }

    # Logout before session revocation
    logout_response = client.post(
        "/logout",
        headers=headers
    )

    assert logout_response.status_code == 200

    # Same token must not work after logout
    response = client.get(
        "/records/1",
        headers=headers
    )

    assert response.status_code == 401
 
def test_oversized_request_rejected(client, user_a):
    headers = {
        "Authorization": f"Bearer {user_a}"
    }

    large_payload = {
        "title": "Large Request",
        "body": "A" * (17 * 1024)
    }

    response = client.post(
        "/records",
        json=large_payload,
        headers=headers
    )

    assert response.status_code == 413  

def test_zero_record_id_returns_400(client, user_a):
    headers = {
        "Authorization": f"Bearer {user_a}"
    }

    response = client.get(
        "/records/0",
        headers=headers
    )

    assert response.status_code == 400


def test_non_integer_record_id_returns_400(client, user_a):
    headers = {
        "Authorization": f"Bearer {user_a}"
    }

    response = client.get(
        "/records/invalid",
        headers=headers
    )

    assert response.status_code == 400
 