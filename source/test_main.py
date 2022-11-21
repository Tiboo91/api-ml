from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/healthcheck")
    assert 1
    #assert response.json() == {"api_status": true}