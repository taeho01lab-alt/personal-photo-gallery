import io
import os
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
    gallery_app.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    gallery_app.init_db()
    return gallery_app.app.test_client()


def register(client, username, password="pass1234"):
    return client.post(
        "/api/users",
        json={
            "username": username,
            "password": password,
            "display_name": username.title(),
            "email": f"{username}@example.com",
        },
    )


def login(client, username, password="pass1234"):
    return client.post("/api/login", json={"username": username, "password": password})


def upload(client, description="Sunset", keywords="travel,summer"):
    return client.post(
        "/api/photos",
        data={
            "description": description,
            "keywords": keywords,
            "photo_password": "photo-pass",
            "photo": (io.BytesIO(b"fake image"), "photo.jpg"),
        },
        content_type="multipart/form-data",
    )


def test_guest_can_view_users_only(client):
    register(client, "alice")

    assert client.get("/api/users").status_code == 200
    assert client.get("/api/photos").status_code == 401
    assert client.get("/api/messages").status_code == 401


def test_login_success_and_failure(client):
    register(client, "alice")

    assert login(client, "alice").status_code == 200
    client.post("/api/logout")
    assert login(client, "alice", "wrong").status_code == 401


def test_photo_upload_search_and_owner_update(client):
    register(client, "alice")
    login(client, "alice")

    response = upload(client, "Mountain sunrise", "nature,hiking")
    assert response.status_code == 201
    photo_id = response.get_json()["photo"]["id"]

    search = client.get("/api/photos?keyword=nature")
    assert search.status_code == 200
    assert len(search.get_json()["photos"]) == 1

    update = client.put(
        f"/api/photos/{photo_id}",
        json={"description": "Updated mountain", "keywords": "hiking"},
    )
    assert update.status_code == 200
    assert update.get_json()["photo"]["description"] == "Updated mountain"


def test_non_owner_cannot_update_photo(client):
    register(client, "alice")
    login(client, "alice")
    photo_id = upload(client).get_json()["photo"]["id"]
    client.post("/api/logout")

    register(client, "bob")
    login(client, "bob")
    response = client.put(
        f"/api/photos/{photo_id}",
        json={"description": "blocked", "keywords": "blocked"},
    )
    assert response.status_code == 403


def test_dm_send_reply_and_delete(client):
    register(client, "alice")
    login(client, "alice")
    photo_id = upload(client).get_json()["photo"]["id"]
    client.post("/api/logout")

    register(client, "bob")
    login(client, "bob")
    sent = client.post(f"/api/photos/{photo_id}/messages", json={"body": "Nice shot!"})
    assert sent.status_code == 201
    message_id = sent.get_json()["message"]["id"]
    client.post("/api/logout")

    login(client, "alice")
    inbox = client.get("/api/messages?box=inbox")
    assert inbox.status_code == 200
    assert inbox.get_json()["messages"][0]["body"] == "Nice shot!"

    reply = client.post(f"/api/messages/{message_id}/reply", json={"body": "Thanks!"})
    assert reply.status_code == 201

    deleted = client.delete(f"/api/messages/{message_id}")
    assert deleted.status_code == 200
    remaining = client.get("/api/messages?box=inbox").get_json()["messages"]
    assert all(message["id"] != message_id for message in remaining)
