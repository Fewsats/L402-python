import os
import sqlite3
from datetime import datetime

from .macaroon_service import MacaroonService

def adapt_datetime(dt):
    return dt.isoformat()

# Register the custom datetime adapter
# This is needed because the default datetime adapter is deprecated in Python 3.12 and later versions
# The custom adapter converts datetime objects to ISO 8601 string format for storage in the database
sqlite3.register_adapter(datetime, adapt_datetime)

class SqliteMacaroonService(MacaroonService):
    """
    SqliteMacaroonService is an SQLite-based credentials service for L402.
    """

    def __init__(self, path=None):
        self.db_path = path or os.path.join(os.path.expanduser('~'), 'authenticator.db')
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS macaroons (
                -- id is the primary key of the table.
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- token_id is ...
                token_id BLOB UNIQUE NOT NULL,

                -- root_key is...
                root_key BLOB NOT NULL,
                        
                -- macaroon is the "admin" base64 encoded macaroon
                macaroon TEXT,

                -- created_at is the date and time when the credentials were
                -- created.
                created_at DATETIME NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS macaroons_token_id_idx ON macaroons (token_id);
        """
        cursor = self.conn.cursor()
        cursor.executescript(create_table_sql)
        self.conn.commit()
    
    async def insert_root_key(self, token_id: bytes, root_key: bytes, macaroon: str):
        insert_sql = """
            INSERT INTO macaroons (
                token_id, root_key, macaroon, created_at
            ) VALUES (
                ?, ?, ?, ?
            );
        """

        created_at = datetime.now()

        cursor = self.conn.cursor()
        cursor.execute(
            (insert_sql), 
            (token_id, root_key, macaroon, created_at),
        )
        self.conn.commit()
    
    async def get_root_key(self, token_id: bytes) -> bytes:
        query_sql = """
            SELECT root_key
            FROM macaroons
            WHERE token_id = ?
        """

        cursor = self.conn.cursor()
        cursor.execute(
            query_sql, (token_id,)
        )

        row = cursor.fetchone()
        if row is None:
            return None

        return row[0]
        
    def __del__(self):
        """
        Close the SQLite connection.
        """
        self.conn.close()