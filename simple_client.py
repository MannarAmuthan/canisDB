import json
import socket

# Connect to the database server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 5012))

try:

    print("Creating table...")
    command = {
        "query": """
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT UNIQUE,
                value TEXT
            )
        """,
        "params": []
    }
    sock.send(json.dumps(command).encode())
    result = json.loads(sock.recv(4096).decode())
    print(f"Create table result: {result}")

    # Insert a test record
    print("\nInserting test data...")
    command = {
        "query": """
            INSERT INTO kv_store (key, value)
            VALUES (?, ?)
        """,
        "params": ["user_1", "John Doe"]
    }
    sock.send(json.dumps(command).encode())
    result = json.loads(sock.recv(4096).decode())
    print(f"Insert result: {result}")

    # Read and display the record
    print("\nReading data...")
    command = {
        "query": "SELECT * FROM kv_store",
        "params": []
    }
    sock.send(json.dumps(command).encode())
    result = json.loads(sock.recv(4096).decode())


    """
    
    prints below
    
    Reading data...

    Key		Value
    ------------------------------
    user_1		John Doe
    """
    if 'rows' in result:
        print("\nKey\t\tValue")
        print("-" * 30)
        for row in result['rows']:
            print(f"{row[0]}\t\t{row[1]}")
    else:
        print("No data found")

finally:
    sock.close()