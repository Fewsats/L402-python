import os
import sqlite3
from datetime import datetime

from .credentials import L402Credentials
from .credentias_service import CredentialsService

def adapt_datetime(dt):
    return dt.isoformat()

# Register the custom datetime adapter
# This is needed because the default datetime adapter is deprecated in Python 3.12 and later versions
# The custom adapter converts datetime objects to ISO 8601 string format for storage in the database
sqlite3.register_adapter(datetime, adapt_datetime)

class SqliteCredentialsService(CredentialsService):
    """
    SqliteCredentialsService is an SQLite-based credentials service for L402.
    """

    def __init__(self, path=None):
        self.db_path = path or os.path.join(os.path.expanduser('~'), 'credentials.db')
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS credentials (
                -- id is the primary key of the table.
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- location is the url for the resource.
                location TEXT NOT NULL,

                -- macaroon is the base64 encoded macaroon needed in the
                -- L402 request header.
                macaroon TEXT NOT NULL,

                -- preimage is the preimage linked to the macaroon payment
                -- hash. Also needed in the L402 request header.
                preimage TEXT,

                -- invoice is the LN invoice that was paid to complete the
                -- credentials.
                invoice TEXT NOT NULL,

                -- created_at is the date and time when the credentials were
                -- created.
                created_at DATETIME NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS credentials_location_index ON credentials (location);
        """
        cursor = self.conn.cursor()
        cursor.executescript(create_table_sql)
        self.conn.commit()
    
    async def store(self, credentials: L402Credentials):
        insert_sql = """
            INSERT INTO credentials (
                location, macaroon, preimage, invoice, created_at
            ) VALUES (
                ?, ?, ?, ?, ?
            );
        """

        location = credentials.location
        macaroon = credentials.macaroon
        preimage = credentials.preimage
        invoice = credentials.invoice
        created_at = datetime.now()

        cursor = self.conn.cursor()
        cursor.execute(
            (insert_sql), 
            (location, macaroon, preimage, invoice, created_at),
        )
        self.conn.commit()
    
    async def get(self, location: str):
        query_sql = """
            SELECT macaroon, preimage, invoice
            FROM credentials
            WHERE location = ?
            ORDER BY created_at DESC
            LIMIT 1
        """

        cursor = self.conn.cursor()
        cursor.execute(
            query_sql, (location,)
        )

        row = cursor.fetchone()
        if row:
            macaroon, preimage, invoice = row
            credentials = L402Credentials(macaroon, preimage, invoice)
            credentials.set_location(location)
            return credentials
        
        return None

    def __del__(self):
        """
        Close the SQLite connection.
        """
        self.conn.close()