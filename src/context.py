class Context:
    """A static class to hold and manage application-wide configuration."""
    _id = None
    _mode = None
    _db_server_port = 5432  # Default database server port
    _grpc_server_port = 50051  # Default gRPC server port
    _server_url = ""

    # Getters and Setters
    @classmethod
    def get_id(cls):
        return cls._id

    @classmethod
    def set_id(cls, value):
        cls._id = value

    @classmethod
    def get_mode(cls):
        return cls._mode

    @classmethod
    def set_mode(cls, value):
        cls._mode = value

    @classmethod
    def get_db_server_port(cls):
        return cls._db_server_port

    @classmethod
    def set_db_server_port(cls, value):
        if not isinstance(value, int):
            raise ValueError("Database server port must be an integer.")
        cls._db_server_port = value

    @classmethod
    def get_grpc_server_port(cls):
        return cls._grpc_server_port

    @classmethod
    def set_grpc_server_port(cls, value):
        if not isinstance(value, int):
            raise ValueError("gRPC server port must be an integer.")
        cls._grpc_server_port = value

    @classmethod
    def get_server_url(cls):
        return cls._server_url

    @classmethod
    def set_server_url(cls, value):
        cls._server_url = value
