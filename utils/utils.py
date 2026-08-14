from enum import StrEnum
import os

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()


def create_connection():
    """Open a Postgres connection from POSTGRES_* env vars (defaults match local compose)."""
    try:
        connection = psycopg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "bernalillo-water-quality"),
            user=os.getenv("POSTGRES_USER", "admin"),
            password=os.getenv("POSTGRES_PASSWORD", "admin"),
        )
        register_vector(connection)
        return connection
    except psycopg.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

class ContaminantValueType(StrEnum):
    AVG_SYSTEM = "avg_system"
    NINETIETH_PERCENTILE = "ninetieth_percentile"
    MAX_LRAA = "max_lraa"
    LOWER_DETECTION_LIMIT = "lower_detection_limit"
    UPPER_DETECTION_LIMIT = "upper_detection_limit"
    MIN_DETECTED = "min_detected"
    MAX_DETECTED = "max_detected"
    AVERAGE_SAN_JUAN = "avg_sjcp"
    MAXIMUM_CONTAMINANT_LEVEL = "mcl"
    MAXIMUM_CONTAMINANT_LEVEL_GOAL = "mclg"
    NUM_SAMPLES_EXCEEDING_ACTION_LEVEL = "num_samples_exceeding_action_level"
    ACTION_LEVEL = "action_level"

class ContaminantValueDescriptions(StrEnum):
  AVG_SYSTEM = "Average detected system wide"
  NINETIETH_PERCENTILE = "Ninetieth percentile"
  MAX_LRAA = "Max LRAA"
  LOWER_DETECTION_LIMIT = "Lower detection limit"
  UPPER_DETECTION_LIMIT = "Upper detection limit"
  MIN_DETECTED = "Minimum detected"
  MAX_DETECTED = "Maximum detected"
  AVERAGE_SAN_JUAN = "Average Detected at San Juan-Chama Drinking Water Plant"
  MAXIMUM_CONTAMINANT_LEVEL = "Maximum contaminant level"
  MAXIMUM_CONTAMINANT_LEVEL_GOAL = "Maximum contaminant level goal"
  NUM_SAMPLES_EXCEEDING_ACTION_LEVEL = "Number of samples exceeding action level"
  ACTION_LEVEL = "Action level"
