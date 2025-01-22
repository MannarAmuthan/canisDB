from db.connector import DBConnector


class WALLogger:
    def __init__(self,
                 database_connector: DBConnector):
        self.database_connector = database_connector

    def init_logger(self):
        setup_commands = [
            {
                "query": """
                        CREATE TABLE IF NOT EXISTS write_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        log_date DATETIME NOT NULL,     
                        query_text TEXT NOT NULL,                
                        query_params TEXT,                      
                        replica_source TEXT NOT NULL 
                        )
                    """
            }
        ]

        for setup_command in setup_commands:
            self.database_connector.execute_query(command=setup_command)
