import datetime
import os

from db.connector import DBConnector
from raft.log import RaftLog


def test_should_prepare_and_commit_logs():
    temp_db = f'test_ignore_temp_func_test.db'
    db_connector: DBConnector = DBConnector(file_path=temp_db)

    raft_log = RaftLog(database_connector=db_connector)
    raft_log.init_logger()

    commands = [
        {
            "query": """
                CREATE TABLE IF NOT EXISTS simple_store (
                    key TEXT UNIQUE,
                    value TEXT
                )
            """,
            "params": []
        },
        {
            "query": """
                INSERT INTO simple_store (key, value)
                    VALUES ('aaa', 'bbb')
                """,
            'params': []
        }
    ]

    unique_ids = ['11', '22']

    for index in range(0, len(commands)):
        raft_log.prepare(
            unique_id=unique_ids[index],
            log_date=datetime.datetime(2025, 3, 30, 0, 0, 0),
            command=commands[index]
        )
    for unique_id in unique_ids:
        raft_log.commit(
            unique_id=unique_id,
            commit_date=datetime.datetime(2025, 3, 30, 0, 0, 0)
        )

    get_all_command = {
        "query": "SELECT * FROM raft_operation_log",
        "params": []
    }

    result = db_connector.execute_query(command=get_all_command)

    try:
        os.remove(temp_db)
    except OSError:
        pass

    assert result == {
        'columns': ['id', 'unique_id', 'query_text', 'query_params', 'status', 'log_date', 'committed_at'],
        'rows': [(1, '11', """
                CREATE TABLE IF NOT EXISTS simple_store (
                    key TEXT UNIQUE,
                    value TEXT
                )
            """, '[]', 'committed', '2025-03-30 00:00:00', '2025-03-30 00:00:00'), (2, '22', """
                INSERT INTO simple_store (key, value)
                    VALUES ('aaa', 'bbb')
                """, '[]', 'committed', '2025-03-30 00:00:00', '2025-03-30 00:00:00')], 'status': 'success'
    }
