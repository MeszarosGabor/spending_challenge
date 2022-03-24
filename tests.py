import unittest.mock as mock
from datetime import datetime as orig_datetime

import pytest

from app import app


############################## FIXTURES ##############################
@pytest.fixture()
def get_app():
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    return app


@pytest.fixture()
def client(get_app):
    return app.test_client()

############################### TESTS ################################
def test_spendings_endpoint_empty_response(client):
        response = client.get("/spendings/")
        assert response.status_code == 200
        assert len(response.json) == 0


MOCKED_DATETIME = mock.MagicMock()
MOCKED_DATETIME.utcnow = lambda: orig_datetime.fromtimestamp(1)
@mock.patch('app.datetime', MOCKED_DATETIME)
def test_POST_spending(client):
    json_={'description': 'test_snack',
                                 'amount': 123,
                                 'currency': 'USD'}
    response = client.post("/add_spending",
                           json=json_)
    assert response._status_code == 200
    response = client.get("/spendings/")
    assert response._status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['spent_at'] == 'Thu, 01 Jan 1970 01:00:01 GMT'


def test_index_page(client):
    response = client.get("/")
    assert response.status_code
    assert b"<h1>Expense TRACKER</h1>" in response.data
    # TODO: extend the page content testing.
    # TODO: test form filling
