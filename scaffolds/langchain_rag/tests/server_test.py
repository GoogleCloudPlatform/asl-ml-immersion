"""Integration tests for server.py"""

from app import server


def test_query():
    server.app.testing = True
    client = server.app.test_client()

    r = client.get("/myapp?query=if+I+were+a+unicorn")
    assert r.status_code == 200
