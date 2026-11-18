import json
import os
import secrets
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

CHANNELS = {"ai": "前沿 AI", "robotics": "机器人 / VLA"}
KINDS = ("新品发布", "研究成果", "厂商预告／预览")
PAPERS = ("预印本", "已正式发表", "未明确")
EVIDENCE = ("仿真", "实机演示", "实机评测", "仿真与实机评测", "未明确")
FIELDS = ("channel", "title", "summary", "source", "source_date", "source_url",
          "kind", "paper", "evidence", "event", "why")
LIMITS = {"title": 120, "summary": 220, "source": 100, "source_url": 2048,
          "event": 5000, "why": 5000}
COLUMNS = ", ".join(FIELDS)
PLACEHOLDERS = ", ".join("?" for _ in FIELDS)


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    return db


def initialize(path, seeds):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with closing(connect(path)) as db, db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS settings (
                name TEXT PRIMARY KEY, value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                channel TEXT NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL,
                source TEXT NOT NULL, source_date TEXT NOT NULL, source_url TEXT NOT NULL,
                kind TEXT NOT NULL, paper TEXT NOT NULL, evidence TEXT NOT NULL,
                event TEXT NOT NULL, why TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('draft', 'published'))
            );
        """)
        db.execute("BEGIN IMMEDIATE")
        db.execute("INSERT OR IGNORE INTO settings VALUES ('session_secret', ?)",
                   (secrets.token_hex(32),))
        if not db.execute("SELECT 1 FROM settings WHERE name = 'seeded'").fetchone():
            db.executemany(
                f"INSERT INTO articles ({COLUMNS}, status) VALUES ({PLACEHOLDERS}, 'published')",
                (tuple(article[field] for field in FIELDS) for article in seeds),
            )
            db.execute("INSERT INTO settings VALUES ('seeded', 'yes')")
        return db.execute("SELECT value FROM settings WHERE name = 'session_secret'").fetchone()[0]


def valid_source_url(value):
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value) or "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in ("https", "http") and bool(parsed.hostname) and parsed.username is None
    except ValueError:
        return False


def article_errors(article, status):
    errors = []
    if article["channel"] not in CHANNELS or article["kind"] not in KINDS:
        errors.append("请选择有效的频道和新闻类型。")
    if article["paper"] not in ("", *PAPERS) or article["evidence"] not in ("", *EVIDENCE):
        errors.append("请选择有效的论文状态和评测方式。")
    if not article["title"]:
        errors.append("请输入标题。")
    for field, limit in LIMITS.items():
        if len(article[field]) > limit:
            errors.append(f"有字段超过了 {limit} 字符的长度限制。")
    if article["source_date"]:
        try:
            if date.fromisoformat(article["source_date"]).isoformat() != article["source_date"]:
                raise ValueError
        except ValueError:
            errors.append("请输入有效的原文发布日期。")
    if article["source_url"] and not valid_source_url(article["source_url"]):
        errors.append("请输入以 https:// 或 http:// 开头的原文链接。")
    required = ("summary", "source", "source_date", "source_url", "event", "why")
    if status == "published" and any(not article[field] for field in required):
        errors.append("发布前请填写摘要、来源、原文发布日期、原文链接和两段详情。")
    return errors


def create_app(database=None):
    app = Flask(__name__)
    path = Path(database) if database else Path(app.instance_path) / "briefing.sqlite3"
    seeds = json.loads((Path(app.root_path) / "seed.json").read_text(encoding="utf-8"))
    app.secret_key = initialize(path, seeds)
    app.config.update(SESSION_COOKIE_SAMESITE="Lax", MAX_CONTENT_LENGTH=128_000,
                      TRUSTED_HOSTS=["127.0.0.1", "localhost"])

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
                return redirect(url_for("login"), code=303)
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
        channel = request.args.get("channel", "ai")
        if channel not in CHANNELS:
            abort(404)
        articles = get_db().execute(
            "SELECT * FROM articles WHERE status = 'published' AND channel = ? "
            "ORDER BY source_date DESC, id DESC", (channel,)
        ).fetchall()
        return render_template("home.html", channel=channel, articles=articles)

    @app.get("/news/<int:article_id>")
    def detail(article_id):
        article = get_db().execute(
            "SELECT * FROM articles WHERE id = ? AND status = 'published'", (article_id,)
        ).fetchone()
        if article is None:
            abort(404)
        return render_template("detail.html", article=article)

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
                session.clear()
                session["admin"] = True
                return redirect(url_for("admin"), code=303)
        return render_template("login.html", setup=setup, error=error), 400 if error else 200

    @app.post("/admin/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"), code=303)

    @app.get("/admin")
    def admin():
        articles = get_db().execute("SELECT * FROM articles ORDER BY status, source_date DESC, id DESC").fetchall()
        return render_template("admin.html", articles=articles)

    @app.route("/admin/new", methods=["GET", "POST"])
    @app.route("/admin/edit/<int:article_id>", methods=["GET", "POST"])
    def edit(article_id=None):
        db = get_db()
        if article_id is None:
            article = {field: "" for field in FIELDS}
            article.update(channel="ai", kind=KINDS[0], status="draft")
        else:
            row = db.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
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
                if article["channel"] == "robotics" and not article["evidence"]:
                    article["evidence"] = "未明确"
                values = tuple(article[field] for field in FIELDS)
                with db:
                    if article_id is None:
                        cursor = db.execute(
                            f"INSERT INTO articles ({COLUMNS}, status) VALUES ({PLACEHOLDERS}, ?)",
                            (*values, action),
                        )
                        article_id = cursor.lastrowid
                    else:
                        assignments = ", ".join(f"{field} = ?" for field in FIELDS)
                        db.execute(f"UPDATE articles SET {assignments}, status = ? WHERE id = ?",
                                   (*values, action, article_id))
                return redirect(url_for("edit", article_id=article_id, saved=action), code=303)

        return render_template("edit.html", article=article, article_id=article_id,
                               errors=errors, kinds=KINDS, papers=PAPERS, evidence=EVIDENCE), 400 if errors else 200

    @app.errorhandler(404)
    def missing(error):
        return render_template("missing.html"), 404

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.environ.get("BRIEFING_PORT", "8765")))
