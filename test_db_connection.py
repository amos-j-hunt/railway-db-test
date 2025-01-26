# test_db_connection.py
import psycopg2
from psycopg2 import sql

def test_connection():
    try:
        # Connection details (use the internal service hostname)
        connection = psycopg2.connect(
            dbname="railway",  # Replace with your database name
            user="postgres",             # Default PostgreSQL user
            password="TbYWKegsfTIyoLteyOQQTPfFORKRGvSb",    # Replace with your database password
            host="postgres.railway.internal",  # Internal hostname
            port="5432"                  # Default PostgreSQL port
        )

        # Test query
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()

        print("Connected successfully to the database!")
        print(f"PostgreSQL version: {db_version[0]}")

        # Clean up
        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_connection()
