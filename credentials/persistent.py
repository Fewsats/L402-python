import sqlite3
import os
from credentials.credentials import L402Credentials  # Import the L402Credentials class

class PersistentStore:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '.credentials.db')
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS credentials (
            -- id is the primary key of the table.
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- url is the url for the resource.
            url TEXT NOT NULL,
            -- method is the method for the resource.
            method TEXT NOT NULL,
            -- macaroon is the base64 encoded macaroon needed in the 
            -- L402 request header.
            macaroon TEXT NOT NULL,
            -- preimage is the preimage linked to the macaroon payment
            -- hash. Also needed in the L402 request header.
            preimage TEXT NOT NULL,
            -- invoice is the LN invoice that was paid to complete the
            -- credentials.
            invoice TEXT NOT NULL,
            
            -- created_at is the date and time when the credentials were
            -- created.
            created_at DATETIME NOT NULL
        );

        CREATE INDEX IF NOT EXISTS credentials_url_method_index ON credentials (url, method);
        """

        self.conn.executescript(create_table_sql)
        self.conn.commit()

    def get_l402_credentials(self, url, method):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT macaroon, preimage, invoice 
            FROM credentials 
            WHERE url = ? AND method = ?
        """, (url, method))
        row = cursor.fetchone()
        if row:
            macaroon, preimage, invoice = row
            return L402Credentials(macaroon, preimage, invoice)
        return None

    def save_l402_credentials(self, url, method, credentials):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO credentials (url, method, macaroon, preimage, invoice, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (url, method, credentials.macaroon, credentials.preimage, credentials.invoice))  # Assuming credentials are stored as a JSON string
        self.conn.commit()

    def __del__(self):
        self.conn.close()
        self.conn.close()