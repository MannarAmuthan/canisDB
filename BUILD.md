
### Building grpc modules

```
sh ./generate.sh
```

change `import replication_pb2 as replication__pb2` to 
`import grpc_generated.replication_pb2 as replication__pb2`