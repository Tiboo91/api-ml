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


def test_fraud_detection():
    response = client.post("/gettoken",data={"username": "clementine", "password": "mandarine"})
    params={
        'purchase_value': 22,
        'age': 35,
        'signup_time':'2022-11-20T21:18:33.518815',
        'purchase_time':'2022-11-21T22:18:33.518863',
        'sex':'Male',
        'browser':'Chrome',
        'source':'SEO'
    }
    header={"Authorization":"Bearer" + " " + response.json()['access_token']}
    response = client.get("/fraudCheck",params=params,headers=header)
    assert response.status_code == 200
    assert response.text.upper() in ('TRUE','FALSE')

