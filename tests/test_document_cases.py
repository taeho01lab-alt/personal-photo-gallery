import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE", str(tmp_path / "gallery.db"))
    monkeypatch.setenv("UPLOAD_FOLDER", str(tmp_path / "uploads"))

    import importlib
    import app as gallery_app

    importlib.reload(gallery_app)
    gallery_app.app.config.update(TESTING=True, SECRET_KEY="document-case-secret")
    gallery_app.init_db()
    return gallery_app.app.test_client()


def create_user(client, username="testuser", password="test1234"):
    return client.post(
        "/api/users",
        json={
            "username": username,
            "password": password,
            "display_name": "Test User",
            "email": f"{username}@example.com",
        },
    )


def login(client, username="testuser", password="test1234"):
    return client.post("/api/login", json={"username": username, "password": password})


def upload_sample_photo(client, description="내 사진", keywords="travel"):
    return client.post(
        "/api/photos",
        data={
            "photo": (io.BytesIO(b"sample image bytes"), "sample.jpg"),
            "description": description,
            "keywords": keywords,
            "photo_password": "photo1234",
        },
        content_type="multipart/form-data",
    )


def test_login_001_user_can_login_with_valid_credentials(client):
    create_user(client)

    response = login(client)
    body = response.get_json()

    assert response.status_code == 200
    assert body["message"] == "로그인 성공"
    assert body["token"]
    assert body["user"]["username"] == "testuser"


def test_token_auth_keeps_protected_api_available_when_cookie_is_unavailable(client):
    create_user(client)
    token = login(client).get_json()["token"]
    client.post("/api/logout")

    response = client.get("/api/photos", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.get_json()["photos"] == []


def test_upload_001_user_can_upload_photo_with_description_and_keyword(client):
    create_user(client)
    login(client)

    response = upload_sample_photo(client)
    body = response.get_json()

    assert response.status_code == 201
    assert body["message"] == "사진 업로드 완료"
    assert body["photo"]["original_filename"] == "sample.jpg"
    assert body["photo"]["description"] == "내 사진"
    assert body["photo"]["keywords"] == ["travel"]


def test_search_001_user_can_search_photo_by_keyword(client):
    create_user(client)
    login(client)
    upload_sample_photo(client)

    response = client.get("/api/photos?keyword=travel")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["photos"]) == 1
    assert body["photos"][0]["description"] == "내 사진"
    assert "travel" in body["photos"][0]["keywords"]


def test_message_001_user_can_send_message_to_photo_owner(client):
    create_user(client, "testuser", "test1234")
    login(client, "testuser", "test1234")
    photo_id = upload_sample_photo(client).get_json()["photo"]["id"]
    client.post("/api/logout")

    create_user(client, "sender", "test1234")
    login(client, "sender", "test1234")

    response = client.post(f"/api/photos/{photo_id}/messages", json={"body": "Hello"})
    body = response.get_json()

    assert response.status_code == 201
    assert body["message"]["body"] == "Hello"
    assert body["message"]["sender_username"] == "sender"
    assert body["message"]["receiver_username"] == "testuser"

    client.post("/api/logout")
    login(client, "testuser", "test1234")
    inbox = client.get("/api/messages?box=inbox").get_json()["messages"]

    assert len(inbox) == 1
    assert inbox[0]["body"] == "Hello"
