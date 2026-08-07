import psycopg
from utils.utils import create_connection


def check_table_exists(connection: psycopg.Connection, table_name: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass(%s) IS NOT NULL", (f"public.{table_name}",))
        return bool(cursor.fetchone()[0])

def create_table(connection: psycopg.Connection, table_name: str, sql: str, ):
    if check_table_exists(connection, table_name):
        print(f"Table {table_name} already exists")
        return True
    else:
      try:
          with connection.cursor() as cursor:
              cursor.execute(sql)
          connection.commit()
          print("Table created successfully")
          return True
      except psycopg.Error as e:
          connection.rollback()
          print(f"Error creating table: {e}")
          return None


def main():
    connection = create_connection()
    if connection is not None:
        print("Connected to the database")
    else:
        print("Failed to connect to the database")
        return

    # Create knowledge base chunks table
    if not create_table(connection, "knowledge_base_chunks", """
        CREATE TABLE IF NOT EXISTS knowledge_base_chunks (
            id SERIAL PRIMARY KEY,
            ingested_date TIMESTAMP NOT NULL,
            report_year SMALLINT NOT NULL CHECK (report_year >= 1900),
            section VARCHAR(255) NOT NULL,
            source_url VARCHAR(255) NOT NULL,
            text TEXT NOT NULL,
            tsv TSVECTOR NOT NULL,
            embedding VECTOR(384) NOT NULL
        )
    """):
        print("Failed to create knowledge base chunks table")

    # create compliance_results table
    if not create_table(connection, "compliance_results", """
        CREATE TABLE IF NOT EXISTS compliance_results (
            id SERIAL PRIMARY KEY,
            report_year SMALLINT NOT NULL CHECK (report_year >= 1900),
            contaminant_code VARCHAR(255),
            contaminant_name VARCHAR(255) NOT NULL,
            sample_year SMALLINT CHECK (sample_year >= 1900),
            sample_year_range VARCHAR(255),
            units VARCHAR(255),
            lower_detection_limit FLOAT,
            upper_detection_limit FLOAT,
            min_detected FLOAT,
            avg_system FLOAT,
            avg_sjcp FLOAT,
            max_detected FLOAT,
            mcl FLOAT,
            mclg FLOAT,
            source_url VARCHAR(255),
            contaminant_source VARCHAR(255),
            max_lraa FLOAT,
            num_samples_exceeding_action_level INT,
            ninetieth_percentile FLOAT,
            action_level FLOAT,
            uses_treatment_technique BOOLEAN NOT NULL
        )
    """):
        print("Failed to create compliance results table")

    connection.close()

if __name__ == "__main__":
    main()