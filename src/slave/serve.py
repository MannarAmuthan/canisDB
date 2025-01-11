from concurrent import futures
import grpc
from grpc_generated import replication_pb2, replication_pb2_grpc


class BridgeServicer(replication_pb2_grpc.BridgeServicer):
    def Replicate(self, request, context):
        print(f"Received request from {request.name}")
        return replication_pb2.Response(message=f"Hello, {request.name}!", status_code=f"100")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replication_pb2_grpc.add_BridgeServicer_to_server(BridgeServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Server starting on port 50051...")
    server.start()
    server.wait_for_termination()