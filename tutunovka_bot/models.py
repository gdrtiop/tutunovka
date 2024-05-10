import psycopg2
from psycopg2 import sql


class PostgreSQLQueries:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect(self):
        try:
            conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            return conn
        except psycopg2.Error as e:
            print("Unable to connect to the database:", e)

    def get_user_fields(self, user_id):
        conn = self.connect()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT *
                    FROM auth_user
                    WHERE id = %s
                    """,
                    (user_id,)
                )
                user_data = cursor.fetchone()
                cursor.close()
                conn.close()
                return user_data
            except psycopg2.Error as e:
                print("Error executing SQL statement:", e)
                return None
