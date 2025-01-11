import argparse
import threading

from master import replicate
from server.server import DatabaseServer
from slave import receive

DEFAULT_DATABASE_SERVER_PORT = 5001


def start_server(port):
    db_server = DatabaseServer(port=port)
    db_server.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode')
    parser.add_argument('-p', '--port')

    parser.add_argument('-gp', '--grpc_port')
    parser.add_argument('-s', '--server_url')
    args = parser.parse_args()

    database_server_port = DEFAULT_DATABASE_SERVER_PORT
    if args.port:
        database_server_port = args.port

    print("Starting database server")
    database_server_thread = threading.Thread(target=start_server, args=(int(database_server_port),))
    database_server_thread.start()

    if args.mode == 'master':
        if args.server_url:
            replicate(args.server_url)
    if args.mode == 'slave':
        if args.grpc_port:
            receive(args.grpc_port)
