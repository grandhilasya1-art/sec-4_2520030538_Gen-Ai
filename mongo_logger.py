import os
from datetime import datetime, timezone
from pymongo import MongoClient


class MongoLogger:
    def __init__(self):
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Force a connection check now so connection errors are clear at startup.
        self.client.admin.command("ping")
        self.db = self.client["llm_monitoring"]
        self.collection = self.db["call_logs"]

    def log_call(self, log_data):
        document = dict(log_data)
        document["timestamp"] = datetime.now(timezone.utc)
        self.collection.insert_one(document)
        print("Call details saved in MongoDB!")

    def close(self):
        self.client.close()
