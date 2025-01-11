set -e

python3 -m grpc_tools.protoc -I./src --python_out=src/grpc_generated/ --grpc_python_out=src/grpc_generated/ src/replication.proto