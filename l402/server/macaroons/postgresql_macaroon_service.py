import psycopg2
from datetime import datetime
from l402.server.macaroons import MacaroonService

class PostgreSQLMacaroonService(MacaroonService):
    def __init__(self, **kwargs):
        self.conn = psycopg2.connect(**kwargs)
        self._create_table()

    def _create_table(self):
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS macaroons (
                id SERIAL PRIMARY KEY,
                token_id BYTEA UNIQUE NOT NULL,
                root_key BYTEA NOT NULL,
                macaroon TEXT,
                created_at TIMESTAMP NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS macaroons_token_id_idx ON macaroons (token_id);
        """
        with self.conn.cursor() as cur:
            cur.execute(create_table_sql)
        self.conn.commit()

    async def insert_root_key(self, token_id: bytes, root_key: bytes, macaroon: str):
        insert_sql = """
            INSERT INTO macaroons (token_id, root_key, macaroon, created_at)
            VALUES (%s, %s, %s, %s);
        """
        created_at = datetime.now()
        with self.conn.cursor() as cur:
            cur.execute(insert_sql, (token_id, root_key, macaroon, created_at))
        self.conn.commit()

    async def get_root_key(self, token_id: bytes) -> bytes:
        query_sql = """
            SELECT root_key
            FROM macaroons
            WHERE token_id = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query_sql, (token_id,))
            row = cur.fetchone()
        return row[0] if row else None

    def __del__(self):
        self.conn.close()