import argparse
import threading

from context import Context
from master import replicate
from db_server.server import DatabaseServer
from slave import receive

DEFAULT_DATABASE_SERVER_PORT = 5012
GRPC_SERVER_PORT = 50051


def start_server(port):
    db_server = DatabaseServer(host='0.0.0.0', port=port)
    db_server.start()


def initialize_and_get_configurations(parsed_args):
    Context.set_id(parsed_args.id)
    Context.set_mode(parsed_args.mode)
    Context.set_db_server_port(int(parsed_args.port) if parsed_args.port else DEFAULT_DATABASE_SERVER_PORT)
    Context.set_grpc_server_port(int(parsed_args.grpc_port) if parsed_args.grpc_port else GRPC_SERVER_PORT)
    Context.set_server_url(parsed_args.server_url if parsed_args.server_url else '')
    Context.set_verbose(parsed_args.verbose if parsed_args.verbose else False)
    Context.set_folder(f"{parsed_args.folder}/{parsed_args.id}" if parsed_args.folder else f"local/{parsed_args.id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode')
    parser.add_argument('-p', '--port')
    parser.add_argument('-id', '--id')

    parser.add_argument('-gp', '--grpc_port')
    parser.add_argument('-s', '--server_url')
    parser.add_argument('-fo', '--folder')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    initialize_and_get_configurations(args)

    print("Starting database db_server")
    database_server_thread = threading.Thread(target=start_server, args=(Context.get_db_server_port(),))
    database_server_thread.start()

    # if args.mode == 'master':
    #     if args.server_url:
    #         replicate(args.server_url)
    # if args.mode == 'slave':
    #     if args.grpc_port:
    #         receive(args.grpc_port)
