# CanisDB

An experimental, lightweight, distributed relational database built using SQLite.

### Quick Start in Local

1. Build and start service

```
docker build -t canis-db -f Dockerfile .
docker-compose -f compose.local.yaml build
docker-compose -f compose.local.yaml up
```

2. Execute below code (example.py)

```python
from canis_client import CanisClient

canis_client = CanisClient()
canis_client.connect("127.0.0.1", 5012)

try:
    print("Creating table...")
    result = canis_client.execute("""
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT UNIQUE,
                value TEXT
            )
        """, [])

    print(f"Create table result: {result}")

    # Insert a test record
    print("\nInserting test data...")
    result = canis_client.execute(
        """
            INSERT INTO kv_store (key, value)
            VALUES (?, ?)
        """,
        ["user_1", "John Doe"]
    )

    print(f"Insert result: {result}")

    # Read and display the record
    print("\nReading data...")
    result = canis_client.execute(
        "SELECT * FROM kv_store",
        []
    )

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
    canis_client.close()

```

### Running functional tests

1. Run above commands to run in local and wait for all containers to span up.
2. `pipenv run functional-test`



