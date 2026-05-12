import os
import sqlite3
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory, session
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("DATABASE", BASE_DIR / "gallery.db"))
UPLOAD_DIR = Path(os.environ.get("UPLOAD_FOLDER", BASE_DIR / "uploads"))
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-gallery-secret"),
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,
)
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:3000", "http://localhost:3000"])


def auth_serializer():
    return URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="gallery-auth")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_db():
    if "db" not in g:
        DATABASE.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        db = get_db()
        with open(BASE_DIR / "schema.sql", encoding="utf-8") as schema:
            db.executescript(schema.read())
        db.commit()


def row_to_dict(row):
    return dict(row) if row else None


def error(message, status=400):
    return jsonify({"error": message}), status


def public_user(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "email": row["email"],
        "created_at": row["created_at"],
    }


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        auth_header = request.headers.get("Authorization", "")
        token = request.args.get("access_token", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
        if token:
            try:
                user_id = auth_serializer().loads(token, max_age=60 * 60 * 8)
            except (BadSignature, SignatureExpired):
                user_id = None

    if not user_id:
        return None
    user = get_db().execute(
        "SELECT id, username, display_name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if not user:
        session.clear()
    return user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            return error("로그인이 필요합니다.", 401)
        return view(user, *args, **kwargs)

    return wrapped


def parse_keywords(raw_value):
    tokens = raw_value if isinstance(raw_value, list) else str(raw_value or "").split(",")
    keywords = []
    seen = set()
    for token in tokens:
        keyword = token.strip().lower()
        if keyword and keyword not in seen:
            seen.add(keyword)
            keywords.append(keyword)
    return keywords


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def attach_keywords(photo_id, keywords):
    db = get_db()
    db.execute("DELETE FROM photo_keywords WHERE photo_id = ?", (photo_id,))
    for keyword in keywords:
        db.execute("INSERT OR IGNORE INTO keywords (name) VALUES (?)", (keyword,))
        keyword_id = db.execute("SELECT id FROM keywords WHERE name = ?", (keyword,)).fetchone()["id"]
        db.execute(
            "INSERT OR IGNORE INTO photo_keywords (photo_id, keyword_id) VALUES (?, ?)",
            (photo_id, keyword_id),
        )


def photo_response(photo_row):
    photo = row_to_dict(photo_row)
    keywords = get_db().execute(
        """
        SELECT k.name
        FROM keywords k
        JOIN photo_keywords pk ON pk.keyword_id = k.id
        WHERE pk.photo_id = ?
        ORDER BY k.name
        """,
        (photo["id"],),
    ).fetchall()
    photo["keywords"] = [keyword["name"] for keyword in keywords]
    photo["url"] = f"/uploads/{photo['stored_filename']}"
    return photo


def message_response(row, viewer_id):
    message = row_to_dict(row)
    message["direction"] = "received" if message["receiver_id"] == viewer_id else "sent"
    if message.get("stored_filename"):
        message["photo_url"] = f"/uploads/{message['stored_filename']}"
    return message


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "database": DATABASE.name})


@app.route("/api/users", methods=["GET"])
def list_users():
    users = get_db().execute(
        "SELECT id, username, display_name, email, created_at FROM users ORDER BY username"
    ).fetchall()
    return jsonify({"users": [public_user(user) for user in users]})


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    display_name = (data.get("display_name") or username).strip()
    email = (data.get("email") or "").strip() or None

    if not username or not password:
        return error("아이디와 비밀번호를 입력해야 합니다.")
    if len(username) < 3:
        return error("아이디는 3자 이상이어야 합니다.")
    if len(password) < 4:
        return error("비밀번호는 4자 이상이어야 합니다.")

    try:
        cursor = get_db().execute(
            """
            INSERT INTO users (username, password_hash, display_name, email, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, generate_password_hash(password), display_name, email, utc_now()),
        )
        get_db().commit()
    except sqlite3.IntegrityError:
        return error("이미 사용 중인 아이디 또는 이메일입니다.", 409)

    user = get_db().execute(
        "SELECT id, username, display_name, email, created_at FROM users WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    return jsonify({"user": public_user(user)}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return error("아이디와 비밀번호를 입력해야 합니다.")

    user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return error("아이디 또는 비밀번호가 올바르지 않습니다.", 401)

    session.clear()
    session["user_id"] = user["id"]
    token = auth_serializer().dumps(user["id"])
    return jsonify({"message": "로그인 성공", "token": token, "user": public_user(user)})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "로그아웃 완료"})


@app.route("/api/me")
def me():
    user = current_user()
    return jsonify({"user": public_user(user) if user else None})


@app.route("/api/photos", methods=["GET"])
@login_required
def list_photos(_user):
    keyword = (request.args.get("keyword") or "").strip().lower()
    db = get_db()

    if keyword:
        photos = db.execute(
            """
            SELECT DISTINCT p.id, p.owner_id, p.original_filename, p.stored_filename,
                   p.description, p.photo_password_hash, p.created_at, p.updated_at,
                   u.username AS owner_username, u.display_name AS owner_display_name
            FROM photos p
            JOIN users u ON u.id = p.owner_id
            LEFT JOIN photo_keywords pk ON pk.photo_id = p.id
            LEFT JOIN keywords k ON k.id = pk.keyword_id
            WHERE k.name LIKE ? OR p.description LIKE ?
            ORDER BY p.created_at DESC
            """,
            (f"%{keyword}%", f"%{keyword}%"),
        ).fetchall()
    else:
        photos = db.execute(
            """
            SELECT p.id, p.owner_id, p.original_filename, p.stored_filename,
                   p.description, p.photo_password_hash, p.created_at, p.updated_at,
                   u.username AS owner_username, u.display_name AS owner_display_name
            FROM photos p
            JOIN users u ON u.id = p.owner_id
            ORDER BY p.created_at DESC
            """
        ).fetchall()

    return jsonify({"photos": [photo_response(photo) for photo in photos]})


@app.route("/api/photos", methods=["POST"])
@login_required
def upload_photo(user):
    image = request.files.get("photo")
    description = (request.form.get("description") or "").strip()
    keywords = parse_keywords(request.form.get("keywords"))
    photo_password = request.form.get("photo_password") or ""

    if not image or image.filename == "":
        return error("업로드할 사진 파일을 선택해야 합니다.")
    if not allowed_file(image.filename):
        return error("jpg, jpeg, png, gif, webp 파일만 업로드할 수 있습니다.")
    if not description or not keywords or not photo_password:
        return error("사진 설명, 키워드, 사진 비밀번호를 모두 입력해야 합니다.")

    original_filename = secure_filename(image.filename)
    extension = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid.uuid4().hex}.{extension}"
    image.save(UPLOAD_DIR / stored_filename)

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO photos
          (owner_id, original_filename, stored_filename, description, photo_password_hash, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"],
            original_filename,
            stored_filename,
            description,
            generate_password_hash(photo_password),
            utc_now(),
            utc_now(),
        ),
    )
    attach_keywords(cursor.lastrowid, keywords)
    db.commit()

    photo = get_photo_row(cursor.lastrowid)
    return jsonify({"message": "사진 업로드 완료", "photo": photo_response(photo)}), 201


@app.route("/api/photos/<int:photo_id>", methods=["GET"])
@login_required
def get_photo(_user, photo_id):
    photo = get_photo_row(photo_id)
    if not photo:
        return error("사진을 찾을 수 없습니다.", 404)
    return jsonify({"photo": photo_response(photo)})


@app.route("/api/photos/<int:photo_id>", methods=["PUT"])
@login_required
def update_photo(user, photo_id):
    data = request.get_json(silent=True) or {}
    photo = get_db().execute("SELECT * FROM photos WHERE id = ?", (photo_id,)).fetchone()
    if not photo:
        return error("사진을 찾을 수 없습니다.", 404)
    if photo["owner_id"] != user["id"]:
        return error("본인 사진만 수정할 수 있습니다.", 403)

    description = (data.get("description") or "").strip()
    keywords = parse_keywords(data.get("keywords"))
    photo_password = data.get("photo_password") or ""
    if not description or not keywords:
        return error("사진 설명과 키워드를 입력해야 합니다.")

    password_hash = photo["photo_password_hash"]
    if photo_password:
        password_hash = generate_password_hash(photo_password)

    db = get_db()
    db.execute(
        """
        UPDATE photos
        SET description = ?, photo_password_hash = ?, updated_at = ?
        WHERE id = ?
        """,
        (description, password_hash, utc_now(), photo_id),
    )
    attach_keywords(photo_id, keywords)
    db.commit()

    return jsonify({"message": "사진 수정 완료", "photo": photo_response(get_photo_row(photo_id))})


def get_photo_row(photo_id):
    return get_db().execute(
        """
        SELECT p.id, p.owner_id, p.original_filename, p.stored_filename,
               p.description, p.photo_password_hash, p.created_at, p.updated_at,
               u.username AS owner_username, u.display_name AS owner_display_name
        FROM photos p
        JOIN users u ON u.id = p.owner_id
        WHERE p.id = ?
        """,
        (photo_id,),
    ).fetchone()


@app.route("/api/photos/<int:photo_id>/messages", methods=["POST"])
@login_required
def send_photo_message(sender, photo_id):
    data = request.get_json(silent=True) or {}
    body = (data.get("body") or "").strip()
    photo = get_db().execute("SELECT id, owner_id FROM photos WHERE id = ?", (photo_id,)).fetchone()

    if not photo:
        return error("사진을 찾을 수 없습니다.", 404)
    if photo["owner_id"] == sender["id"]:
        return error("본인 게시물에는 DM을 보낼 수 없습니다.")
    if not body:
        return error("메시지 내용을 입력해야 합니다.")

    message_id = create_message(sender["id"], photo["owner_id"], photo_id, body, None)
    return jsonify({"message": message_response(get_message_row(message_id), sender["id"])}), 201


@app.route("/api/messages", methods=["POST"])
@login_required
def send_message(sender):
    data = request.get_json(silent=True) or {}
    receiver_id = data.get("receiver_id")
    photo_id = data.get("photo_id")
    body = (data.get("body") or "").strip()

    try:
        receiver_id = int(receiver_id)
        photo_id = int(photo_id) if photo_id else None
    except (TypeError, ValueError):
        return error("수신자 또는 사진 ID가 올바르지 않습니다.")

    if receiver_id == sender["id"]:
        return error("자기 자신에게는 메시지를 보낼 수 없습니다.")
    if not body:
        return error("메시지 내용을 입력해야 합니다.")
    if not get_db().execute("SELECT id FROM users WHERE id = ?", (receiver_id,)).fetchone():
        return error("대상 사용자를 찾을 수 없습니다.", 404)
    if photo_id and not get_db().execute("SELECT id FROM photos WHERE id = ?", (photo_id,)).fetchone():
        return error("연결할 사진을 찾을 수 없습니다.", 404)

    message_id = create_message(sender["id"], receiver_id, photo_id, body, None)
    return jsonify({"message": message_response(get_message_row(message_id), sender["id"])}), 201


@app.route("/api/messages", methods=["GET"])
@login_required
def list_messages(user):
    box = request.args.get("box", "all")
    if box == "sent":
        where_clause = "m.sender_id = ? AND m.sender_deleted = 0"
        params = (user["id"],)
    elif box == "inbox":
        where_clause = "m.receiver_id = ? AND m.receiver_deleted = 0"
        params = (user["id"],)
    else:
        where_clause = "((m.receiver_id = ? AND m.receiver_deleted = 0) OR (m.sender_id = ? AND m.sender_deleted = 0))"
        params = (user["id"], user["id"])

    messages = get_db().execute(
        f"""
        SELECT m.id, m.sender_id, su.username AS sender_username,
               m.receiver_id, ru.username AS receiver_username,
               m.photo_id, p.original_filename AS photo_filename, p.stored_filename,
               m.parent_id, m.body, m.is_read, m.created_at
        FROM messages m
        JOIN users su ON su.id = m.sender_id
        JOIN users ru ON ru.id = m.receiver_id
        LEFT JOIN photos p ON p.id = m.photo_id
        WHERE {where_clause}
        ORDER BY m.created_at DESC
        """,
        params,
    ).fetchall()
    return jsonify({"messages": [message_response(message, user["id"]) for message in messages]})


@app.route("/api/messages/<int:message_id>/reply", methods=["POST"])
@login_required
def reply_message(user, message_id):
    data = request.get_json(silent=True) or {}
    body = (data.get("body") or "").strip()
    original = get_db().execute(
        "SELECT * FROM messages WHERE id = ? AND (sender_id = ? OR receiver_id = ?)",
        (message_id, user["id"], user["id"]),
    ).fetchone()
    if not original:
        return error("메시지를 찾을 수 없습니다.", 404)
    if not body:
        return error("답장 내용을 입력해야 합니다.")

    receiver_id = original["sender_id"] if original["receiver_id"] == user["id"] else original["receiver_id"]
    reply_id = create_message(user["id"], receiver_id, original["photo_id"], body, message_id)
    return jsonify({"message": message_response(get_message_row(reply_id), user["id"])}), 201


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
@login_required
def delete_message(user, message_id):
    message = get_db().execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
    if not message:
        return error("메시지를 찾을 수 없습니다.", 404)
    if user["id"] not in (message["sender_id"], message["receiver_id"]):
        return error("메시지를 삭제할 권한이 없습니다.", 403)

    field = "sender_deleted" if message["sender_id"] == user["id"] else "receiver_deleted"
    get_db().execute(f"UPDATE messages SET {field} = 1 WHERE id = ?", (message_id,))
    get_db().commit()
    return jsonify({"message": "메시지 삭제 완료"})


@app.route("/api/messages/<int:message_id>/read", methods=["PATCH"])
@login_required
def mark_message_read(user, message_id):
    cursor = get_db().execute(
        "UPDATE messages SET is_read = 1 WHERE id = ? AND receiver_id = ?",
        (message_id, user["id"]),
    )
    get_db().commit()
    if cursor.rowcount == 0:
        return error("메시지를 찾을 수 없습니다.", 404)
    return jsonify({"message": "메시지를 읽음 처리했습니다."})


def create_message(sender_id, receiver_id, photo_id, body, parent_id):
    cursor = get_db().execute(
        """
        INSERT INTO messages (sender_id, receiver_id, photo_id, parent_id, body, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (sender_id, receiver_id, photo_id, parent_id, body, utc_now()),
    )
    get_db().commit()
    return cursor.lastrowid


def get_message_row(message_id):
    return get_db().execute(
        """
        SELECT m.id, m.sender_id, su.username AS sender_username,
               m.receiver_id, ru.username AS receiver_username,
               m.photo_id, p.original_filename AS photo_filename, p.stored_filename,
               m.parent_id, m.body, m.is_read, m.created_at
        FROM messages m
        JOIN users su ON su.id = m.sender_id
        JOIN users ru ON ru.id = m.receiver_id
        LEFT JOIN photos p ON p.id = m.photo_id
        WHERE m.id = ?
        """,
        (message_id,),
    ).fetchone()


@app.route("/uploads/<path:filename>")
@login_required
def uploaded_file(_user, filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=int(os.environ.get("PORT", "5000")))
