from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_healthcheck():
    response = client.get("/healthCheck")
    assert response.status_code == 200
    assert response.json() == {"api_status": True}

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200

def test_authentification_p():
    response = client.post(
        "/gettoken",
        data={"username": "clementine", "password": "mandarine"},
    )
    assert response.status_code == 200

def test_authentification_n():
    response = client.post(
        "/gettoken",
        data={"username": "clementine", "password": "mandarinee"},
    )
    assert response.status_code == 401
    assert response.json()['detail']=='Incorrect username or password'