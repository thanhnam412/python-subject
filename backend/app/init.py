import os
import psycopg2

host = "localhost"

try:
    be_port = os.environ["BE_PORT"]
    db_port = os.environ["DB_PORT"]
    db_user = os.environ["DB_USER"]
    db_name = os.environ["DB_NAME"]
    db_password = ""
except:
    be_port = "8080"
    db_port = "5432"
    db_user = "cps"
    db_name = "test"
    db_password = ""


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
        )
        print(f"--> connect success {host,db_port,db_user,db_name} ")
        return conn
    except:
        print("--> connect fail")
        return conn
