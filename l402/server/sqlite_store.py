import sqlite3
import os

from abc import ABC, abstractmethod

class Store(ABC):
    @abstractmethod
    def create_root_key(self, token_id, root_key):
        """Stores the root key for a given token ID."""
        pass

    @abstractmethod
    def get_root_key(self, token_id):
        """Retrieves the root key for a given token ID."""
        pass

class SQLiteStore:
    def __init__(self, path=None):
        self.db_path = path or os.path.join(os.path.expanduser('~'), 'authenticator.db')
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS root_keys (
            token_id TEXT PRIMARY KEY,
            root_key BLOB NOT NULL
        );
        """
        self.conn.execute(create_table_sql)
        self.conn.commit()

    def create_root_key(self, token_id, root_key):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO root_keys (token_id, root_key)
            VALUES (?, ?)
        """, (token_id.hex(), root_key))
        self.conn.commit()

    def get_root_key(self, token_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT root_key FROM root_keys WHERE token_id = ?
        """, (token_id.hex(),))
        row = cursor.fetchone()
        if row:
            return row[0]
        return None

    def __del__(self):
        self.conn.close()