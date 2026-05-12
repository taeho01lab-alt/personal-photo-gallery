import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000";
const AUTH_TOKEN_KEY = "personal_gallery_auth_token";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const token = window.localStorage.getItem(AUTH_TOKEN_KEY);
  const headers = options.body instanceof FormData ? {} : { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers,
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(data.error || "요청 처리 중 오류가 발생했습니다.", response.status);
  }
  return data;
}

function imageUrl(path) {
  return `${API_BASE_URL}${path}`;
}

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState("users");
  const [notice, setNotice] = useState("");
  const [users, setUsers] = useState([]);
  const [photos, setPhotos] = useState([]);
  const [messages, setMessages] = useState([]);
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState({ username: "", password: "", display_name: "", email: "" });
  const [keyword, setKeyword] = useState("");
  const [uploadForm, setUploadForm] = useState({ description: "", keywords: "", photo_password: "", photo: null });
  const [editingPhoto, setEditingPhoto] = useState(null);
  const [messageDrafts, setMessageDrafts] = useState({});
  const [replyDrafts, setReplyDrafts] = useState({});

  const parsedUploadKeywords = useMemo(
    () => uploadForm.keywords.split(",").map((item) => item.trim()).filter(Boolean),
    [uploadForm.keywords]
  );

  const handleRequestError = useCallback((error) => {
    if (error.status === 401) {
      window.localStorage.removeItem(AUTH_TOKEN_KEY);
      setCurrentUser(null);
      setActiveTab("auth");
      setPhotos([]);
      setMessages([]);
      setNotice("세션이 만료되었습니다. 다시 로그인해 주세요.");
      return;
    }
    setNotice(error.message);
  }, []);

  function changeTab(tab) {
    setActiveTab(tab);
    setNotice("");
  }

  const loadUsers = useCallback(async () => {
    const data = await request("/api/users");
    setUsers(data.users);
  }, []);

  const loadPhotos = useCallback(async (nextKeyword = keyword) => {
    try {
      const suffix = nextKeyword ? `?keyword=${encodeURIComponent(nextKeyword)}` : "";
      const data = await request(`/api/photos${suffix}`);
      setPhotos(data.photos);
    } catch (error) {
      handleRequestError(error);
    }
  }, [handleRequestError, keyword]);

  const loadMessages = useCallback(async () => {
    try {
      const data = await request("/api/messages?box=all");
      setMessages(data.messages);
    } catch (error) {
      handleRequestError(error);
    }
  }, [handleRequestError]);

  useEffect(() => {
    request("/api/me").then((data) => setCurrentUser(data.user)).catch(() => setCurrentUser(null));
    loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    if (currentUser && activeTab === "gallery") {
      loadPhotos();
    }
    if (currentUser && activeTab === "messages") {
      loadMessages();
    }
  }, [currentUser, activeTab, loadPhotos, loadMessages]);

  async function submitAuth(event) {
    event.preventDefault();
    try {
      if (authMode === "register") {
        await request("/api/users", { method: "POST", body: JSON.stringify(authForm) });
      }
      const data = await request("/api/login", {
        method: "POST",
        body: JSON.stringify({ username: authForm.username, password: authForm.password }),
      });
      window.localStorage.setItem(AUTH_TOKEN_KEY, data.token);
      setCurrentUser(data.user);
      setActiveTab("gallery");
      setNotice("로그인되었습니다.");
      loadUsers();
    } catch (error) {
      setNotice(error.message);
    }
  }

  async function logout() {
    try {
      await request("/api/logout", { method: "POST" });
    } finally {
      window.localStorage.removeItem(AUTH_TOKEN_KEY);
    }
    setCurrentUser(null);
    setActiveTab("users");
    setPhotos([]);
    setMessages([]);
    setNotice("로그아웃되었습니다.");
  }

  async function uploadPhoto(event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append("description", uploadForm.description);
    formData.append("keywords", parsedUploadKeywords.join(","));
    formData.append("photo_password", uploadForm.photo_password);
    if (uploadForm.photo) {
      formData.append("photo", uploadForm.photo);
    }

    try {
      await request("/api/photos", { method: "POST", body: formData });
      setUploadForm({ description: "", keywords: "", photo_password: "", photo: null });
      event.target.reset();
      setNotice("사진이 업로드되었습니다.");
      loadPhotos("");
    } catch (error) {
      handleRequestError(error);
    }
  }

  async function updatePhoto(event) {
    event.preventDefault();
    try {
      await request(`/api/photos/${editingPhoto.id}`, {
        method: "PUT",
        body: JSON.stringify({
          description: editingPhoto.description,
          keywords: editingPhoto.keywordsText,
          photo_password: editingPhoto.photo_password,
        }),
      });
      setEditingPhoto(null);
      setNotice("사진 정보가 수정되었습니다.");
      loadPhotos();
    } catch (error) {
      handleRequestError(error);
    }
  }

  async function sendDm(photoId) {
    try {
      await request(`/api/photos/${photoId}/messages`, {
        method: "POST",
        body: JSON.stringify({ body: messageDrafts[photoId] || "" }),
      });
      setMessageDrafts({ ...messageDrafts, [photoId]: "" });
      setNotice("DM을 보냈습니다.");
    } catch (error) {
      handleRequestError(error);
    }
  }

  async function replyMessage(messageId) {
    try {
      await request(`/api/messages/${messageId}/reply`, {
        method: "POST",
        body: JSON.stringify({ body: replyDrafts[messageId] || "" }),
      });
      setReplyDrafts({ ...replyDrafts, [messageId]: "" });
      setNotice("답장을 보냈습니다.");
      loadMessages();
    } catch (error) {
      handleRequestError(error);
    }
  }

  async function deleteMessage(messageId) {
    try {
      await request(`/api/messages/${messageId}`, { method: "DELETE" });
      setNotice("메시지가 삭제되었습니다.");
      loadMessages();
    } catch (error) {
      handleRequestError(error);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">SW Project Team 7</p>
          <h1>Personal Photo Gallery</h1>
        </div>
        <div className="session">
          {currentUser ? (
            <>
              <strong>{currentUser.display_name || currentUser.username}</strong>
              <button onClick={logout}>로그아웃</button>
            </>
          ) : (
            <button onClick={() => changeTab("auth")}>로그인</button>
          )}
        </div>
      </header>

      <nav className="tabs">
        <button className={activeTab === "users" ? "active" : ""} onClick={() => changeTab("users")}>
          사용자 목록
        </button>
        <button className={activeTab === "auth" ? "active" : ""} onClick={() => changeTab("auth")}>
          회원가입/로그인
        </button>
        {currentUser && (
          <>
            <button className={activeTab === "gallery" ? "active" : ""} onClick={() => changeTab("gallery")}>
              사진 갤러리
            </button>
            <button className={activeTab === "messages" ? "active" : ""} onClick={() => changeTab("messages")}>
              메시지
            </button>
          </>
        )}
      </nav>

      {notice && <p className="notice">{notice}</p>}

      {activeTab === "users" && (
        <section className="panel">
          <div className="section-title">
            <h2>사용자 목록</h2>
            <span>비회원도 조회 가능</span>
          </div>
          <div className="user-grid">
            {users.length === 0 && <p className="muted">등록된 사용자가 없습니다.</p>}
            {users.map((user) => (
              <article className="user-card" key={user.id}>
                <strong>{user.display_name || user.username}</strong>
                <small>@{user.username}</small>
              </article>
            ))}
          </div>
        </section>
      )}

      {activeTab === "auth" && (
        <section className="panel narrow">
          <div className="segmented">
            <button className={authMode === "login" ? "selected" : ""} onClick={() => setAuthMode("login")}>
              로그인
            </button>
            <button className={authMode === "register" ? "selected" : ""} onClick={() => setAuthMode("register")}>
              회원가입
            </button>
          </div>
          <form className="form" onSubmit={submitAuth}>
            <label>
              아이디
              <input value={authForm.username} onChange={(e) => setAuthForm({ ...authForm, username: e.target.value })} />
            </label>
            <label>
              비밀번호
              <input type="password" value={authForm.password} onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })} />
            </label>
            {authMode === "register" && (
              <>
                <label>
                  표시 이름
                  <input value={authForm.display_name} onChange={(e) => setAuthForm({ ...authForm, display_name: e.target.value })} />
                </label>
                <label>
                  이메일
                  <input type="email" value={authForm.email} onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })} />
                </label>
              </>
            )}
            <button className="primary">{authMode === "login" ? "로그인" : "회원가입 후 로그인"}</button>
          </form>
        </section>
      )}

      {activeTab === "gallery" && currentUser && (
        <section className="workspace">
          <form className="panel form upload-panel" onSubmit={uploadPhoto}>
            <h2>사진 업로드</h2>
            <label>
              사진
              <input type="file" accept="image/*" onChange={(e) => setUploadForm({ ...uploadForm, photo: e.target.files[0] })} />
            </label>
            <label>
              설명
              <textarea value={uploadForm.description} onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })} />
            </label>
            <label>
              키워드
              <input value={uploadForm.keywords} onChange={(e) => setUploadForm({ ...uploadForm, keywords: e.target.value })} placeholder="travel, summer" />
            </label>
            <label>
              사진 비밀번호
              <input type="password" value={uploadForm.photo_password} onChange={(e) => setUploadForm({ ...uploadForm, photo_password: e.target.value })} />
            </label>
            <button className="primary">업로드</button>
          </form>

          <div className="gallery-column">
            <form className="search-bar" onSubmit={(e) => { e.preventDefault(); loadPhotos(keyword); }}>
              <input placeholder="키워드 검색" value={keyword} onChange={(e) => setKeyword(e.target.value)} />
              <button>검색</button>
            </form>
            <div className="photo-grid">
              {photos.map((photo) => (
                <article className="photo-card" key={photo.id}>
                  <img src={imageUrl(photo.url)} alt={photo.description} />
                  <div className="photo-body">
                    <strong>{photo.description}</strong>
                    <p>{photo.keywords.map((item) => `#${item}`).join(" ")}</p>
                    <small>업로더: {photo.owner_display_name || photo.owner_username}</small>
                    {photo.owner_id === currentUser.id ? (
                      <button onClick={() => setEditingPhoto({ ...photo, keywordsText: photo.keywords.join(", "), photo_password: "" })}>
                        수정
                      </button>
                    ) : (
                      <div className="dm-box">
                        <textarea value={messageDrafts[photo.id] || ""} onChange={(e) => setMessageDrafts({ ...messageDrafts, [photo.id]: e.target.value })} placeholder="업로더에게 DM" />
                        <button onClick={() => sendDm(photo.id)}>DM 전송</button>
                      </div>
                    )}
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}

      {activeTab === "messages" && currentUser && (
        <section className="panel">
          <div className="section-title">
            <h2>메시지함</h2>
            <span>받은 메시지와 보낸 답장</span>
          </div>
          <div className="message-list">
            {messages.length === 0 && <p className="muted">메시지가 없습니다.</p>}
            {messages.map((message) => (
              <article className="message-card" key={message.id}>
                {message.photo_url && <img src={imageUrl(message.photo_url)} alt={message.photo_filename || "photo"} />}
                <div>
                  <strong>{message.direction === "received" ? message.sender_username : `나 -> ${message.receiver_username}`}</strong>
                  <p>{message.body}</p>
                  <small>{new Date(message.created_at).toLocaleString("ko-KR")}</small>
                  <div className="reply-row">
                    <input value={replyDrafts[message.id] || ""} onChange={(e) => setReplyDrafts({ ...replyDrafts, [message.id]: e.target.value })} placeholder="답장" />
                    <button onClick={() => replyMessage(message.id)}>답장</button>
                    <button className="danger" onClick={() => deleteMessage(message.id)}>삭제</button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      {editingPhoto && (
        <div className="modal">
          <form className="panel form modal-body" onSubmit={updatePhoto}>
            <h2>사진 수정</h2>
            <label>
              설명
              <textarea value={editingPhoto.description} onChange={(e) => setEditingPhoto({ ...editingPhoto, description: e.target.value })} />
            </label>
            <label>
              키워드
              <input value={editingPhoto.keywordsText} onChange={(e) => setEditingPhoto({ ...editingPhoto, keywordsText: e.target.value })} />
            </label>
            <label>
              새 사진 비밀번호
              <input type="password" value={editingPhoto.photo_password} onChange={(e) => setEditingPhoto({ ...editingPhoto, photo_password: e.target.value })} placeholder="변경하지 않으려면 비워두세요" />
            </label>
            <div className="button-row">
              <button type="button" onClick={() => setEditingPhoto(null)}>취소</button>
              <button className="primary">저장</button>
            </div>
          </form>
        </div>
      )}
    </main>
  );
}

export default App;
