import json
import socket
from time import sleep
from typing import Dict, Any


class LocalDatabaseClient:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def execute(self, query: str, params: list = None) -> Dict[str, Any]:
        """Execute a query on the database db_server"""
        if params is None:
            params = []

        command = {
            "query": query,
            "params": params
        }

        self.socket.send(json.dumps(command).encode())
        response = self.socket.recv(4096).decode()
        return json.loads(response)

    def close(self):
        """Close the client connection"""
        self.socket.close()


try:
    client_rep_one = LocalDatabaseClient("127.0.0.1", 5012)
    client_rep_two = LocalDatabaseClient("127.0.0.1", 5013)
    client_rep_three = LocalDatabaseClient("127.0.0.1", 5014)
    client_rep_four = LocalDatabaseClient("127.0.0.1", 5015)

    # Create table
    print("Creating table...")
    result = client_rep_three.execute("""
        CREATE TABLE IF NOT EXISTS central_kv_store (
            key TEXT UNIQUE,
            value TEXT
        )
    """)
    print(f"Create table result: {result}")

    # Clear any existing data for clean test
    print("\nCleaning existing data...")
    result = client_rep_three.execute("DELETE FROM central_kv_store")
    print(f"Clean data result: {result}")

    # Insert operations (Create)
    print("\nInserting test data...")
    test_data = [
        ("user_1", "John Doe"),
        ("user_2", "Jane Smith"),
        ("settings_theme", "dark"),
        ("api_key", "abc123xyz")
    ]

    for key, value in test_data:
        result = client_rep_three.execute("""
            INSERT INTO central_kv_store (key, value)
            VALUES (?, ?)
        """, [key, value])  # Using list instead of tuple for JSON serialization
        print(f"Insert result for {key}: {result}")

    # Read operations
    print("\nReading individual records...")
    result = client_rep_three.execute("SELECT value FROM central_kv_store WHERE key = ?", ["user_1"])
    print(f"Read result for user_1: {result}")

    # Update operations
    print("\nUpdating records...")
    result = client_rep_three.execute("""
        UPDATE central_kv_store
        SET value = ?
        WHERE key = ?
    """, ["light", "settings_theme"])
    print(f"Update result: {result}")

    # Delete operations
    print("\nDeleting a record...")
    result = client_rep_three.execute("DELETE FROM central_kv_store WHERE key = ?", ["api_key"])
    print(f"Delete result: {result}")


    result = client_rep_three.execute("""
        INSERT INTO central_kv_store (key, value)
        VALUES ('random', random())
    """, [])

    # Final select to verify all operations
    print("\nFinal state of the database:")
    results = client_rep_three.execute("SELECT * FROM central_kv_store ORDER BY key")
    print("\nKey\t\tValue")
    print("-" * 30)

    if 'rows' in results:
        for row in results['rows']:
            print(f"{row[0]}\t\t{row[1]}")


        def final_assert(client, rep_one):
            final_check = client.execute("SELECT COUNT(*) FROM central_kv_store")
            if 'rows' in final_check and final_check['rows']:
                count = final_check['rows'][0][0]
                expected_count = 3  # After all operations
                assert count == expected_count, f"Expected {expected_count} records, found {count}"
                print(f"\nAll tests completed successfully in {rep_one}!")


        final_assert(client_rep_one, "rep one")
        final_assert(client_rep_two, "rep two")
        final_assert(client_rep_three, "rep three")
        final_assert(client_rep_four, "rep four")

    else:
        print("No rows returned or unexpected response format")

    client_rep_three.close()

except ConnectionRefusedError:
    print("Connection failed - db_server might not be running")
except json.JSONDecodeError:
    print("Received invalid JSON response from db_server")
except Exception as e:
    print(f"Error: {str(e)}")
