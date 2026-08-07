import psycopg

def create_connection():
    try:
        return psycopg.connect("postgresql://admin:admin@localhost:5432/bernalillo-water-quality")
    except psycopg.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None