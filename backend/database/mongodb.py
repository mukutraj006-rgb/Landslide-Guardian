import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

logger = logging.getLogger(__name__)

# Resolve backend/.env reliably, even when Uvicorn uses a reload subprocess.
BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"
load_dotenv(ENV_FILE)

MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise RuntimeError(
        f"MONGODB_URI is missing. Create {ENV_FILE} and add your MongoDB Atlas URI."
    )


class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        try:
            self.client.admin.command("ping")
            self.db = self.client["landslide_guardian"]

            self.users = self.db["users"]
            self.locations = self.db["locations"]
            self.environmental_data = self.db["environmental_data"]
            self.risk_assessments = self.db["risk_assessments"]
            self.alerts = self.db["alerts"]
            self.citizens = self.db["citizens"]

            # Useful indexes for the prototype's most common queries.
            self.risk_assessments.create_index([("timestamp", -1)])
            self.alerts.create_index([("timestamp", -1)])
            self.alerts.create_index([("risk_score", -1)])
            self.citizens.create_index([("location", 1)])

            self.is_connected = True
            logger.info("MongoDB Atlas connected successfully.")
        except Exception as exc:
            self.client.close()
            logger.exception("MongoDB Atlas connection failed.")
            raise RuntimeError(
                "Could not connect to MongoDB Atlas. Check the URI, "
                "database user, and Atlas Network Access IP allowlist."
            ) from exc


def clean_document(doc):
    if not doc:
        return None
    result = dict(doc)
    result.pop("_id", None)
    return result


db_manager = DatabaseManager()
