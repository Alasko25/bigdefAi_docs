# app/logging/mongodb_logger.py
import logging
from datetime import datetime
# from app.database.elasticsearch import es
from app.logging.mongo_connection import collection

class MongoDBHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        if collection is None:
            raise Exception("MongoDB collection non initialisée")
        self.collection = collection

    def emit(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "category": getattr(record, "category", "general"),
            "message": record.getMessage(),
            "user_id": getattr(record, "user_id", None),
            "bank_id": getattr(record, "bank_id", None),
            "transaction_id": getattr(record, "transaction_id", None),
            "alert_id": getattr(record, "alert_id", None),
            "details": getattr(record, "details", {})
        }
        if self.collection is None:
            return  # Ignore si la collection n'est pas initialisée
        try:
            self.collection.insert_one(log_entry)
            # es.index(
            #     index="transactions-logs",
            #     id=log_entry["transaction_id"],
            #     body=log_entry
            # )
        except Exception as e:
            print(f"[Erreur] Échec de l'insertion du log dans MongoDB/Elasticsearch : {e}")