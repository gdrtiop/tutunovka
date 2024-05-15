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
                "postgres://gampayff:vgD1z59fxABGyAN-GLkjNB_YGPL0G0Im@abul.db.elephantsql.com/gampayff"
            )
            return conn
        except psycopg2.Error as e:
            print("Unable to connect to the database:", e)

    def get_user_fields(self, password, username):
        conn = self.connect()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT *
                    FROM "public"."auth_user"
                    WHERE (password = %s) AND (username = %s)
                    """,
                    (password, username,)
                )
                user_data = cursor.fetchone()
                cursor.close()
                conn.close()
                return user_data
            except psycopg2.Error as e:
                print("Error executing SQL statement:", e)
                return None

    def get_route_fields(self, user_id):
        conn = self.connect()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT *
                    FROM "public"."Private_Routes"
                    WHERE author_id = %s AND date_in = (select min(date_in) from "public"."Private_Routes" )
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

    def get_routes(self):
        conn = self.connect()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT *
                    FROM "public"."Private_Routes"
                    """,
                )
                user_data = cursor.fetchone()
                cursor.close()
                conn.close()
                return user_data
            except psycopg2.Error as e:
                print("Error executing SQL statement:", e)
                return None