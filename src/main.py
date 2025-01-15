import argparse
import threading

from master import replicate
from server.server import DatabaseServer
from slave import receive

DEFAULT_DATABASE_SERVER_PORT = 5001
GRPC_SERVER_PORT = 5002


def start_server(port):
    db_server = DatabaseServer(host='0.0.0.0',port=port)
    db_server.start()


def initialize_and_get_configurations(parsed_args):
    return {
        'mode': parsed_args.mode,
        'db_server_port': int(parsed_args.port) if parsed_args.port else DEFAULT_DATABASE_SERVER_PORT,
        'grpc_server_port': parsed_args.grpc_port if parsed_args.grpc_port else GRPC_SERVER_PORT,
        'server_url': parsed_args.server_url if parsed_args.server_url else ''
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode')
    parser.add_argument('-p', '--port')

    parser.add_argument('-gp', '--grpc_port')
    parser.add_argument('-s', '--server_url')
    args = parser.parse_args()

    configurations = initialize_and_get_configurations(args)

    print("Starting database server")
    database_server_thread = threading.Thread(target=start_server, args=(configurations['db_server_port'],))
    database_server_thread.start()

    # if args.mode == 'master':
    #     if args.server_url:
    #         replicate(args.server_url)
    # if args.mode == 'slave':
    #     if args.grpc_port:
    #         receive(args.grpc_port)
