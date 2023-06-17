import psycopg2
import os

class Database:
    def connect():
        try:
            conn = psycopg2.connect(
                host=os.getenv('DATABASE_HOST'),
                port=os.getenv('DATABASE_PORT'),
                database=os.getenv('DATABASE_NAME'),
                user=os.getenv('DATABASE_USER'),
                password=os.getenv('DATABASE_PASSWORD')
            )

            print("Success Database Connection")
            return conn

        except (Exception, psycopg2.Error) as error:
            print("Connection Error", error)
