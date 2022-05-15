from multiprocessing import Process

from starlette.testclient import TestClient
from main import app

def test_server_returns_token():
    client = TestClient(app)
    with client.websocket_connect("/ws/match?name=bbb", ) as websocket:
        data = websocket.receive_json()
        assert data.get('token')


def second_client(token):
    print("inside")
    client2 = TestClient(app)
    with client2.websocket_connect(f"/ws/match?name=bbb&token={token}", ) as websocket2:
        print(websocket2)
        token_data2 = websocket2.receive_json()
    #     players2 = websocket2.receive_json()
    #     rules2 = websocket2.receive_json()
    #     players3 = websocket1.receive_json()
    #     start1 = websocket1.send_json({"type":"START"})
    #     start2 = websocket1.receive_json()
    #     start3 = websocket2.receive_json()

def start_client(token):
    p = Process(target=second_client, args=(token,))
    p.start()
    return p

def test_host_exits_when_he_is_alone_in_room():
    client1 = TestClient(app)
    with client1.websocket_connect("/ws/match?name=aaa", ) as websocket1:
        token_data1 = websocket1.receive_json()
        token = token_data1.get("token")
        print(token)
        players1 = websocket1.receive_json()
        rules1 = websocket1.receive_json()
        p = start_client(token)

    p.kill()



