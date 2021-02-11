from singleton import Singleton
import psycopg2
import logging
import config


@Singleton
class Database:

    def __init__(self):
        self.host = config.DATABASE_HOST
        self.username = config.DATABASE_USERNAME
        self.password = config.DATABASE_PASSWORD
        self.port = config.DATABASE_PORT
        self.dbname = config.DATABASE_NAME
        self.conn = None

    def connect(self):
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    port=self.port,
                    database=self.dbname,
                    sslmode="disable"
                )
            except psycopg2.DatabaseError as e:
                logging.error(e)
                raise e
            finally:
                logging.info('Connection opened successfully.')

    def select_rows(self, query):
        self.connect()
        with self.conn.cursor() as cur:
            cur.execute(query)
            records = [row for row in cur.fetchall()]
            return records

    def execute(self, query):
        self.connect()
        with self.conn.cursor() as cur:
            cur.execute(query)

    def commit(self):
        with self.conn.cursor() as cur:
            cur.close()
        self.conn.commit()

    def close(self):
        with self.conn.cursor() as cur:
            cur.close()

    def init_table(self):
        self.execute("CREATE TABLE IF NOT EXISTS ngram_en(ngram text NOT NULL, count double precision, "
                     "CONSTRAINT ngramen_pkey PRIMARY KEY (ngram));")
        self.execute("CREATE TABLE IF NOT EXISTS ngram_de(ngram text NOT NULL, count double precision, "
                     "CONSTRAINT ngramde_pkey PRIMARY KEY (ngram));")
        self.commit()
