import grpc
from grpc_generated import replication_pb2, replication_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = replication_pb2_grpc.BridgeStub(channel)
        response = stub.Replicate(replication_pb2.Command(name='World'))
        print(response.message)
        print(response.status_code)
