import sqlite3
import threading
from typing import Dict, Any


class DBConnector:
    def __init__(self, file_path: str):
        self.conn = sqlite3.connect(file_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

    def execute_query(self, command: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            try:
                query = command.get("query")
                params = command.get("params", [])

                self.cursor.execute(query, params)

                if query.lower().startswith(("select", "pragma")):
                    results = self.cursor.fetchall()
                    columns = [description[0] for description in self.cursor.description]
                    return {
                        "status": "success",
                        "columns": columns,
                        "rows": results
                    }
                else:
                    self.conn.commit()
                    return {
                        "status": "success",
                        "affected_rows": self.cursor.rowcount
                    }

            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
