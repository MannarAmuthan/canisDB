import random

from tests.functional.canis_client import CanisClient


def test_canis():
    setup_commands = [
        {
            "query": """
                CREATE TABLE IF NOT EXISTS central_kv_store (
                    key TEXT UNIQUE,
                    value TEXT
                )
            """
        },
        {
            "query": "DELETE FROM central_kv_store"
        },
        {
            "query": """
            INSERT INTO central_kv_store (key, value)
                VALUES (?, ?)
            """,
            "param_list": [
                ["user_1", "John Doe"],
                ["user_2", "iiiiiiyyyyyyttttttrrrrreeeewwwwwaaaammmmmm"],
                ["user_3", "98"]
            ]
        },
        {
            "query": """
                INSERT INTO central_kv_store (key, value)
                    VALUES ('zzz', random())
                """
        },
        {
            "query": """
                UPDATE central_kv_store
                SET value = ?
                WHERE key = ?
                """,
            "param_list": [
                ["99", "user_3"]
            ]
        }

    ]

    client_rep_one = CanisClient()
    client_rep_one.connect("127.0.0.1", 5012)
    client_rep_two = CanisClient()
    client_rep_two.connect("127.0.0.1", 5013)
    client_rep_three = CanisClient()
    client_rep_three.connect("127.0.0.1", 5014)
    client_rep_four = CanisClient()
    client_rep_four.connect("127.0.0.1", 5015)

    clients = [client_rep_one, client_rep_two, client_rep_three, client_rep_four]
    for command in setup_commands:
        param_list = command.get('param_list', [[]])
        for param in param_list:
            random_client = random.choice(clients)
            random_client.execute(command['query'], param)

    index = 0

    random_values = []

    for _c in [client_rep_four, client_rep_three, client_rep_two, client_rep_one]:
        results = client_rep_three.execute("SELECT * FROM central_kv_store ORDER BY key", params=[])

        print("-" * 30)

        assert results['columns'] == ['key', 'value']

        assert results['rows'][0] == ['user_1', 'John Doe']
        assert results['rows'][1] == ['user_2', 'iiiiiiyyyyyyttttttrrrrreeeewwwwwaaaammmmmm']
        assert results['rows'][2] == ['user_3', '99']
        assert results['rows'][3][0] == 'zzz'
        random_values.append(results['rows'][3][1])

        index += 1

        print(f"Assertion done in {index}")

    assert all(x == random_values[0] for x in random_values)

    client_rep_one.close()
    client_rep_two.close()
    client_rep_three.close()
    client_rep_four.close()
