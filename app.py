import os
import re
import secrets
import sqlite3
from contextlib import closing
from datetime import date
from io import BytesIO
from pathlib import Path

from flask import Flask, Response, abort, g, redirect, render_template, request, session, url_for
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash

CHANNELS = {"thoughts": "我的思考", "exam": "考研历程", "essays": "小随笔"}
FIELDS = ("channel", "title", "body", "written_on")
COLUMNS = ", ".join(FIELDS)
PLACEHOLDERS = ", ".join("?" for _ in FIELDS)
IMAGE_MARKER = re.compile(r"\[图片:([a-f0-9]{32})\]")
IMAGE_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
IMAGE_LIMIT = 10 * 1024 * 1024


def body_parts(body):
    for index, content in enumerate(IMAGE_MARKER.split(body)):
        yield index % 2 == 1, content



def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    return db


def initialize(path):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with closing(connect(path)) as db, db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS settings (
                name TEXT PRIMARY KEY, value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY, mime TEXT NOT NULL, data BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                channel TEXT NOT NULL, title TEXT NOT NULL,
                body TEXT NOT NULL, written_on TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('draft', 'published'))
            );
        """)
        db.execute("BEGIN IMMEDIATE")
        db.execute("INSERT OR IGNORE INTO settings VALUES ('session_secret', ?)",
                   (secrets.token_hex(32),))
        return db.execute("SELECT value FROM settings WHERE name = 'session_secret'").fetchone()[0]


def article_errors(article, status):
    errors = []
    if article["channel"] not in CHANNELS:
        errors.append("请选择有效的栏目。")
    if not 1 <= len(article["title"]) <= 120:
        errors.append("请填写标题，最多 120 字。")
    if status == "published" and not article["body"]:
        errors.append("写好正文后就可以发表。")
    try:
        if date.fromisoformat(article["written_on"]).isoformat() != article["written_on"]:
            raise ValueError
    except ValueError:
        errors.append("请填写有效的写作日期。")
    return errors


def create_app(database=None):
    app = Flask(__name__)
    path = Path(database) if database else Path(app.instance_path) / "briefing.sqlite3"
    app.secret_key = initialize(path)
    app.config.update(SESSION_COOKIE_SAMESITE="Lax", MAX_CONTENT_LENGTH=1_000_000,
                      TRUSTED_HOSTS=["127.0.0.1", "localhost"])

    app.add_template_filter(lambda body: IMAGE_MARKER.sub("", body).strip(), "article_excerpt")

    def get_db():
        if "db" not in g:
            g.db = connect(path)
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        return session["csrf"]

    @app.context_processor
    def template_values():
        return {"channels": CHANNELS, "csrf_token": csrf_token}

    @app.before_request
    def protect_admin():
        if request.path == "/admin" or request.path.startswith("/admin/"):
            if request.endpoint != "login" and not session.get("admin"):
                if request.endpoint == "edit" and request.method == "GET" and request.path == "/admin/new":
                    session["new_channel"] = request.args.get("channel", "thoughts")
                return redirect(url_for("login"), code=303)
        if request.endpoint == "upload_image":
            request.max_content_length = IMAGE_LIMIT + 65536
        if request.method == "POST":
            token = session.get("csrf")
            if not token or not secrets.compare_digest(token.encode(), request.form.get("csrf", "").encode()):
                abort(400)

    @app.after_request
    def prevent_admin_cache(response):
        if request.path.startswith("/admin"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def home():
        channel = request.args.get("channel", "thoughts")
        if channel not in CHANNELS:
            abort(404)
        articles = get_db().execute(
            "SELECT * FROM entries WHERE status = 'published' AND channel = ? "
            "ORDER BY written_on DESC, id DESC", (channel,)
        ).fetchall()
        return render_template("home.html", channel=channel, articles=articles)

    @app.get("/entry/<int:article_id>")
    def detail(article_id):
        article = get_db().execute(
            "SELECT * FROM entries WHERE id = ? AND status = 'published'", (article_id,)
        ).fetchone()
        if article is None:
            abort(404)
        return render_template("detail.html", article=article, parts=body_parts(article["body"]))

    @app.post("/admin/images")
    def upload_image():
        upload = request.files.get("image")
        if upload is None:
            return {"error": "请选择一张图片。"}, 400
        data = upload.stream.read(IMAGE_LIMIT + 1)
        if len(data) > IMAGE_LIMIT:
            return {"error": "每张图片最大 10 MB。"}, 413
        try:
            with Image.open(BytesIO(data), formats=tuple(IMAGE_FORMATS)) as image:
                mime = IMAGE_FORMATS[image.format]
                if image.width * image.height > 25_000_000:
                    return {"error": "图片分辨率过高，请缩小后重试。"}, 400
                image.load()
        except (OSError, SyntaxError, ValueError, Image.DecompressionBombError):
            return {"error": "请选择有效的 JPG、PNG 或 WebP 图片。"}, 400

        image_id = secrets.token_hex(16)
        db = get_db()
        with db:
            db.execute("INSERT INTO images VALUES (?, ?, ?)", (image_id, mime, data))
        return {"id": image_id}, 201

    @app.get("/image/<image_id>")
    def article_image(image_id):
        db = get_db()
        if not session.get("admin") and not db.execute(
            "SELECT 1 FROM entries WHERE status = 'published' AND instr(body, ?) > 0 LIMIT 1",
            (f"[图片:{image_id}]",),
        ).fetchone():
            abort(404)
        image = db.execute("SELECT mime, data FROM images WHERE id = ?", (image_id,)).fetchone()
        if image is None:
            abort(404)
        return Response(image["data"], mimetype=image["mime"], headers={
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "private, no-store",
        })

    @app.route("/admin/login", methods=["GET", "POST"])
    def login():
        if session.get("admin"):
            return redirect(url_for("admin"))
        db = get_db()
        credential = db.execute("SELECT value FROM settings WHERE name = 'admin_password'").fetchone()
        setup = credential is None
        error = None
        if request.method == "POST":
            password = request.form.get("password", "")
            if setup:
                if not 12 <= len(password) <= 256:
                    error = "请设置 12 到 256 个字符的密码。"
                elif password != request.form.get("confirmation"):
                    error = "两次输入的密码不一致。"
                else:
                    with db:
                        created = db.execute(
                            "INSERT OR IGNORE INTO settings VALUES ('admin_password', ?)",
                            (generate_password_hash(password),),
                        ).rowcount
                    if not created:
                        return redirect(url_for("login"), code=303)
            elif len(password) > 256 or not check_password_hash(credential[0], password):
                error = "密码不正确，请重试。"
            if not error:
                channel = session.pop("new_channel", None)
                session.clear()
                session["admin"] = True
                if channel in CHANNELS:
                    return redirect(url_for("edit", channel=channel), code=303)
                return redirect(url_for("admin"), code=303)
        return render_template("login.html", setup=setup, error=error), 400 if error else 200

    @app.post("/admin/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"), code=303)

    @app.get("/admin")
    def admin():
        articles = get_db().execute("SELECT * FROM entries ORDER BY status, written_on DESC, id DESC").fetchall()
        return render_template("admin.html", articles=articles)

    @app.route("/admin/new", methods=["GET", "POST"])
    @app.route("/admin/edit/<int:article_id>", methods=["GET", "POST"])
    def edit(article_id=None):
        db = get_db()
        if article_id is None:
            article = {field: "" for field in FIELDS}
            channel = request.args.get("channel", "thoughts")
            article.update(channel=channel if channel in CHANNELS else "thoughts", written_on=date.today().isoformat(), status="draft")
        else:
            row = db.execute("SELECT * FROM entries WHERE id = ?", (article_id,)).fetchone()
            if row is None:
                abort(404)
            article = dict(row)

        errors = []
        if request.method == "POST":
            action = request.form.get("action")
            if action not in ("draft", "published"):
                abort(400)
            article.update({field: request.form.get(field, "").strip() for field in FIELDS})
            errors = article_errors(article, action)
            if not errors:
                values = tuple(article[field] for field in FIELDS)
                with db:
                    if article_id is None:
                        cursor = db.execute(
                            f"INSERT INTO entries ({COLUMNS}, status) VALUES ({PLACEHOLDERS}, ?)",
                            (*values, action),
                        )
                        article_id = cursor.lastrowid
                    else:
                        assignments = ", ".join(f"{field} = ?" for field in FIELDS)
                        db.execute(f"UPDATE entries SET {assignments}, status = ? WHERE id = ?",
                                   (*values, action, article_id))
                return redirect(url_for("edit", article_id=article_id, saved=action), code=303)

        return render_template("edit.html", article=article, article_id=article_id,
                               errors=errors), 400 if errors else 200

    @app.errorhandler(404)
    def missing(error):
        return render_template("missing.html"), 404

    return app


if __name__ == "__main__":
    from waitress import serve

    port = int(os.environ.get("BRIEFING_PORT", "8765"))
    print(f"我的手记正在监听 127.0.0.1:{port}", flush=True)
    serve(create_app(), host="127.0.0.1", port=port)
