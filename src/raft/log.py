import json
from datetime import datetime
from typing import Dict, Any

from db.connector import DBConnector


class RaftLog:
    def __init__(self,
                 database_connector: DBConnector):

        self.database_connector = database_connector

    def init_logger(self):
        setup_commands = [
            {
                "query": """
                    CREATE TABLE raft_operation_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_id TEXT NOT NULL UNIQUE,
                        query_text TEXT NOT NULL,                
                        query_params TEXT,
                        status TEXT NOT NULL CHECK(status IN ('prepared', 'committed', 'aborted')),
                        log_date DATETIME NOT NULL,    
                        committed_at DATETIME
                    )
                    """
            }
        ]

        for setup_command in setup_commands:
            self.database_connector.execute_query(command=setup_command)

    def prepare(self,
                unique_id: str,
                log_date: datetime,
                command: Dict[str, Any]):
        insert_command = {
            "query": """
            INSERT INTO raft_operation_log (unique_id, query_text,query_params, status, log_date) 
                VALUES (?, ?, ? ,'prepared', ?)
            """,
            "params": [
                unique_id,
                command['query'],
                json.dumps(command['params']),
                log_date
            ]
        }

        result = self.database_connector.execute_query(insert_command)

        if result['status'] != 'success':
            raise Exception(f"Prepare failed for {unique_id}")

    def commit(self,
               unique_id: str,
               commit_date: datetime,
               ):

        get_command = {
            "query": "SELECT query_text, query_params FROM raft_operation_log WHERE unique_id = ? AND status = 'prepared'",
            "params": [unique_id]
        }
        result = self.database_connector.execute_query(get_command)

        if result['status'] != 'success':
            raise Exception(f"Commit failed for {unique_id}")

        if len(result['rows']) != 1:
            raise Exception(f"Could not find valid logs to commit for {unique_id}")

        query_text = result['rows'][0][0]
        query_params = json.loads(result['rows'][0][1])

        execute_command = {
            "query": query_text,
            "params": query_params
        }

        self.database_connector.execute_query(execute_command)

        commit_command = {
            "query": """
                UPDATE raft_operation_log
                SET status='committed', committed_at=?
                WHERE unique_id=?
            """,
            "params": [
                commit_date,
                unique_id
            ]
        }

        self.database_connector.execute_query(commit_command)
