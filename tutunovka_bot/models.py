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
                    WHERE author_id = %s
                    AND date_in = (
                        SELECT min(date_in)
                        FROM "public"."Private_Routes"
                        WHERE date_in >= CURRENT_DATE
                    )
                    """,
                    (user_id,)
                )
                user_data = cursor.fetchone()
                cursor.close()
                conn.close()
                return user_data if user_data else None
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

    def get_user_by_tg_username(self, tg_username):
        conn = self.connect()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT *
                    FROM "auth_user"
                    WHERE tg_username = %s
                    """,
                    (tg_username,)
                )
                user_data = cursor.fetchone()
                cursor.close()
                conn.close()
                return user_data
            except psycopg2.Error as e:
                print("Error executing SQL statement:", e)
                return None

    def update_tg_username(self, user_id, new_tg_username):
        conn = self.connect()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE "auth_user"
                    SET tg_username = %s
                    WHERE id = %s
                    """,
                    (new_tg_username, user_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return True
            except psycopg2.Error as e:
                print("Error executing SQL statement:", e)
                return False

    def delete_tg_username(self, tg_user_id):
        conn = self.connect()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE "auth_user"
                    SET tg_username = NULL
                    WHERE tg_username = %s
                    """,
                    (tg_user_id,)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return True
            except psycopg2.Error as e:
                print("Error executing SQL statement:", e)
                return False
