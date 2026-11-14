
import os
import json
import sqlite3
from functools import wraps
from werkzeug.utils import secure_filename

from flask import (
    Flask, g, session, redirect, url_for, request,
    render_template, abort, flash, jsonify
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
MAX_CONTENT = 1_000_000  # Maximum saved Delta JSON size in bytes


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-change-me"
)
app.config["DB_PATH"] = DB_PATH


# -------------------------
# DATABASE
# -------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(app.config["DB_PATH"])
    try:
        db.execute("PRAGMA foreign_keys = ON")

        with open(
            os.path.join(BASE_DIR, "schema.sql"),
            encoding="utf-8"
        ) as f:
            db.executescript(f.read())

        db.commit()
    finally:
        db.close()


# -------------------------
# AUTHENTICATION
# -------------------------

def current_user():
    uid = session.get("user_id")

    if uid is None:
        return None

    return get_db().execute(
        "SELECT id, username FROM users WHERE id = ?",
        (uid,)
    ).fetchone()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        g.user = current_user()

        if g.user is None:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    db = get_db()

    if request.method == "POST":
        username = request.form.get("username", "").strip()

        user = db.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user is None:
            return "Unknown user", 400

        session.clear()
        session["user_id"] = user["id"]

        return redirect(url_for("index"))

    users = db.execute(
        "SELECT username FROM users ORDER BY username"
    ).fetchall()

    return render_template("login.html", users=users)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------
# DOCUMENT ACCESS
# -------------------------

def get_doc_for_user(doc_id, user_id):
    row = get_db().execute(
        """
        SELECT d.*,
               CASE
                   WHEN d.owner_id = :uid THEN 'owner'
                   ELSE 'shared'
               END AS role
        FROM documents d
        WHERE d.id = :doc
          AND (
              d.owner_id = :uid
              OR EXISTS (
                  SELECT 1
                  FROM shares s
                  WHERE s.document_id = d.id
                    AND s.user_id = :uid
              )
          )
        """,
        {"doc": doc_id, "uid": user_id},
    ).fetchone()

    return (row, row["role"]) if row else (None, None)


# -------------------------
# DASHBOARD
# -------------------------

@app.route("/")
@login_required
def index():
    db = get_db()

    owned = db.execute(
        """
        SELECT id, title, updated_at
        FROM documents
        WHERE owner_id = ?
        ORDER BY updated_at DESC
        """,
        (g.user["id"],)
    ).fetchall()

    shared = db.execute(
        """
        SELECT d.id, d.title, d.updated_at,
               u.username AS owner
        FROM documents d
        JOIN shares s ON s.document_id = d.id
        JOIN users u ON u.id = d.owner_id
        WHERE s.user_id = ?
        ORDER BY d.updated_at DESC
        """,
        (g.user["id"],)
    ).fetchall()

    return render_template(
        "dashboard.html",
        user=g.user,
        owned=owned,
        shared=shared
    )

MAX_UPLOAD = 500_000  # 500 KB: under the save cap, keeps Quill responsive
ALLOWED_EXT = {".txt", ".md"}

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD + 64 * 1024

@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    f = request.files.get("file")
    if f is None or not f.filename:
        flash("Please select a file.", "error")
        return redirect(url_for("index"))

    name = os.path.basename(f.filename.replace("\\", "/"))
    stem, ext = os.path.splitext(name)
    if ext.lower() not in ALLOWED_EXT:
        flash("Only .txt and .md files are supported.", "error")
        return redirect(url_for("index"))

    raw = f.read(MAX_UPLOAD + 1)          # never read more than limit + 1
    if len(raw) > MAX_UPLOAD:
        flash("File too large (max 500 KB).", "error")
        return redirect(url_for("index"))

    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
    if not text.endswith("\n"):
        text += "\n"

    title = (stem.strip() or "Imported document")[:120]
    db = get_db()
    cur = db.execute(
        "INSERT INTO documents (title, content, owner_id) VALUES (?, ?, ?)",
        (title, json.dumps({"ops": [{"insert": text}]}, ensure_ascii=False), g.user["id"]),
    )
    db.commit()
    return redirect(url_for("open_doc", doc_id=cur.lastrowid))

# -------------------------
# CREATE DOCUMENT
# -------------------------

@app.route("/docs/new", methods=["POST"])
@login_required
def new_doc():
    db = get_db()

    cur = db.execute(
        """
        INSERT INTO documents (title, owner_id)
        VALUES (?, ?)
        """,
        ("Untitled document", g.user["id"])
    )

    db.commit()

    return redirect(
        url_for("open_doc", doc_id=cur.lastrowid)
    )


# -------------------------
# OPEN DOCUMENT
# -------------------------

@app.route("/docs/<int:doc_id>")
@login_required
def open_doc(doc_id):
    doc, role = get_doc_for_user(
        doc_id, g.user["id"]
    )

    if doc is None:
        abort(404)

    # Decode the saved Quill Delta.
    try:
        initial_content = (
            json.loads(doc["content"])
            if doc["content"]
            else {"ops": [{"insert": "\n"}]}
        )
    except (ValueError, TypeError):
        initial_content = {"ops": [{"insert": "\n"}]}

    shared_with = []

    if role == "owner":
        shared_with = get_db().execute(
            """
            SELECT u.username
            FROM shares s
            JOIN users u ON u.id = s.user_id
            WHERE s.document_id = ?
            ORDER BY u.username
            """,
            (doc_id,)
        ).fetchall()

    return render_template(
        "editor.html",
        doc=doc,
        role=role,
        user=g.user,
        shared_with=shared_with,
        initial_content=initial_content
    )


# -------------------------
# SAVE DOCUMENT
# -------------------------

@app.route("/docs/<int:doc_id>/save", methods=["POST"])
@login_required
def save_doc(doc_id):
    doc, role = get_doc_for_user(
        doc_id, g.user["id"]
    )

    if doc is None:
        abort(404)

    # Both owners and shared users can edit.
    data = request.get_json(silent=True) or {}
    content = data.get("content")

    if (
        not isinstance(content, dict)
        or not isinstance(content.get("ops"), list)
    ):
        return jsonify(error="Invalid content"), 400

    try:
        content_json = json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False
        )
    except (TypeError, ValueError):
        return jsonify(error="Invalid content"), 400

    if len(content_json.encode("utf-8")) > MAX_CONTENT:
        return jsonify(error="Document too large"), 413

    db = get_db()

    db.execute(
        """
        UPDATE documents
        SET content = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (content_json, doc_id)
    )

    db.commit()

    return jsonify(ok=True)


# -------------------------
# RENAME DOCUMENT
# -------------------------

@app.route("/docs/<int:doc_id>/rename", methods=["POST"])
@login_required
def rename_doc(doc_id):
    doc, role = get_doc_for_user(
        doc_id, g.user["id"]
    )

    if doc is None:
        abort(404)

    if role != "owner":
        abort(403)

    title = request.form.get("title", "").strip()

    if not title or len(title) > 120:
        flash(
            "Title must be 1 to 120 characters.",
            "error"
        )
    else:
        db = get_db()

        db.execute(
            """
            UPDATE documents
            SET title = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, doc_id)
        )

        db.commit()
        flash("Document renamed.", "success")

    return redirect(
        url_for("open_doc", doc_id=doc_id)
    )


# -------------------------
# SHARE DOCUMENT
# -------------------------

@app.route("/docs/<int:doc_id>/share", methods=["POST"])
@login_required
def share_doc(doc_id):
    db = get_db()

    doc, role = get_doc_for_user(
        doc_id, g.user["id"]
    )

    if doc is None:
        abort(404)

    if role != "owner":
        abort(403)

    username = request.form.get(
        "username", ""
    ).strip()

    if not username:
        flash("Please enter a username.", "error")
        return redirect(
            url_for("open_doc", doc_id=doc_id)
        )

    target = db.execute(
        "SELECT id, username FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if target is None:
        flash("User does not exist.", "error")
        return redirect(
            url_for("open_doc", doc_id=doc_id)
        )

    if target["id"] == g.user["id"]:
        flash(
            "You cannot share a document with yourself.",
            "error"
        )
        return redirect(
            url_for("open_doc", doc_id=doc_id)
        )

    existing = db.execute(
        """
        SELECT id FROM shares
        WHERE document_id = ? AND user_id = ?
        """,
        (doc_id, target["id"])
    ).fetchone()

    if existing:
        flash(
            "This document has already been shared with that user.",
            "error"
        )
        return redirect(
            url_for("open_doc", doc_id=doc_id)
        )

    try:
        db.execute(
            """
            INSERT INTO shares (document_id, user_id)
            VALUES (?, ?)
            """,
            (doc_id, target["id"])
        )
        db.commit()

    except sqlite3.IntegrityError:
        db.rollback()
        flash(
            "This document has already been shared with that user.",
            "error"
        )
        return redirect(
            url_for("open_doc", doc_id=doc_id)
        )

    flash(
        f"Document successfully shared with {username}.",
        "success"
    )

    return redirect(
        url_for("open_doc", doc_id=doc_id)
    )


# -------------------------
# START APPLICATION
# -------------------------

init_db()

if __name__ == "__main__":
    app.run(debug=True)
