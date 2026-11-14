import pytest
from app import app, init_db, get_db, get_doc_for_user


@pytest.fixture
def db(tmp_path):
    app.config["DB_PATH"] = str(tmp_path / "test.db")
    init_db()
    with app.app_context():
        yield get_db()


def test_sharing_access(db):
    db.execute("INSERT INTO documents (title, owner_id) VALUES ('T', 1)")
    db.commit()

    assert get_doc_for_user(1, 1)[1] == "owner"
    assert get_doc_for_user(1, 2) == (None, None)

    db.execute("INSERT INTO shares (document_id, user_id) VALUES (1, 2)")
    db.commit()

    assert get_doc_for_user(1, 2)[1] == "shared"
    assert get_doc_for_user(1, 3) == (None, None)