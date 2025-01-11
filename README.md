

### Running in Local

```
pipenv install
```

Start as slave process

```
python3 src/main.py slave --grpc_port=50051
```

Start another process as master server

```
python3 src/main.py master --server_url="localhost:50051"
```


### Build and run in Dockerfile

`docker build -t "canis-db" -f Dockerfile .`
