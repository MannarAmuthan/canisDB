import json
from datetime import datetime
from typing import Dict, Any

from db.connector import DBConnector


class WALLogger:
    def __init__(self,
                 database_connector: DBConnector):
        self.log_number = 1
        self.database_connector = database_connector

    def init_logger(self):
        setup_commands = [
            {
                "query": """
                        CREATE TABLE IF NOT EXISTS write_logs (
                        log_number INTEGER PRIMARY KEY,
                        log_date DATETIME NOT NULL,     
                        query_text TEXT NOT NULL,                
                        query_params TEXT
                        )
                    """
            }
        ]

        for setup_command in setup_commands:
            self.database_connector.execute_query(command=setup_command)

    def log(self,
            log_date: datetime,
            command: Dict[str, Any]):
        insert_command = {
            "query": """
            INSERT INTO write_logs (log_number, log_date, query_text, query_params)
                VALUES (?, ?, ?, ?)
            """,
            "params": [
                self.log_number,
                log_date,
                command['query'],
                json.dumps(command['params'])
            ]
        }

        self.log_number += 1

        self.database_connector.execute_query(insert_command)
