import requests

def authenticate_database(model_key, password):
    url = "http://127.0.0.1:5000/"
    resp = requests.post(url+"auth_db", json={
        "model_key" : model_key,
        "password" : password
    })
    JSON = resp.json()
    assert JSON['ok'], 'invalid model_key or password'
    return JSON['username']

def authenticate_aqmp(model_key, password):
    url = "http://127.0.0.1:5000/"
    resp = requests.post(url+"auth_amqp", json={
        "model_key" : model_key,
        "password" : password
    })
    JSON = resp.json()
    assert JSON['ok'], 'invalid model_key or password'
    return JSON['amqp_url']
