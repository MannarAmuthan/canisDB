import json


def send_json(connected_socket, data: dict):
    connected_socket.send(json.dumps(data).encode())