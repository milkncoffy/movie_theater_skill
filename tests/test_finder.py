import json
import pytest

import finder_app


@pytest.fixture
def client():
    finder_app.app.config['TESTING'] = True

    with finder_app.app.test_client() as client:
        yield client


def test_init_request(client):
    with open('init_request_body.json') as f:
        request = json.load(f)
    response = client.post('/', json=request)
    assert response.status_code == 200


def test_movie_request(client):
    with open('movie_request_body.json') as f:
        request = json.load(f)
    response = client.post('/', json=request)
    assert response.status_code == 200
