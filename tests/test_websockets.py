from starlette.testclient import TestClient
from main import app

def test_server_returns_token():
    client = TestClient(app)
    with client.websocket_connect("/ws/match") as websocket:
        data = websocket.receive_json()
        assert data.get('token')


def test_host_exits_when_he_is_alone_in_room():
    client = TestClient(app)
    with client.websocket_connect("/ws/match") as websocket:
        data = websocket.receive_json()
        websocket.send_json({"exit": True})

        try:
             client.close()
        except AttributeError:
            assert True
        assert False