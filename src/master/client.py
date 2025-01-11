import grpc
from grpc_generated import replication_pb2, replication_pb2_grpc


def run(master_server_url):
    with grpc.insecure_channel(master_server_url) as channel:
        stub = replication_pb2_grpc.BridgeStub(channel)
        response = stub.Replicate(replication_pb2.Command(name='World'))
        print(response.message, response.status_code)
