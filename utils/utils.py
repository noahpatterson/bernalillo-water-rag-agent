import psycopg
from pgvector.psycopg import register_vector

def create_connection():
    try:
        connection = psycopg.connect(
            "postgresql://admin:admin@localhost:5432/bernalillo-water-quality"
        )
        register_vector(connection)
        return connection
    except psycopg.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None