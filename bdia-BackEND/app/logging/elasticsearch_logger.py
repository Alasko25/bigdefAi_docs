import logging
import json
from elasticsearch import Elasticsearch
from app.core.config import settings
import datetime
import socket

class ElasticsearchHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        # Valider les paramètres
        if not settings.ELASTICSEARCH_URL:
            raise ValueError("ELASTICSEARCH_URL is not set in settings")
        if not settings.LOGSTASH_HOST:
            raise ValueError("LOGSTASH_HOST is not set in settings")

        # Initialiser Elasticsearch
        try:
            self.es = Elasticsearch(
                [settings.ELASTICSEARCH_URL],
                verify_certs=False,
                timeout=30
            )
            if not self.es.ping():
                raise ConnectionError("Failed to connect to Elasticsearch")
        except Exception as e:
            logging.error(f"Elasticsearch initialization failed: {e}")
            self.es = None

        self.index = "bigdefend-logs"
        self.logstash_host = settings.LOGSTASH_HOST
        self.sock = None

        # Initialiser la connexion Logstash
        try:
            host, port = self.logstash_host.split(':')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, int(port)))
        except Exception as e:
            logging.error(f"Logstash connection failed: {e}")
            self.sock = None

    def emit(self, record):
        try:
            log_entry = {
                "@timestamp": datetime.datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "category": getattr(record, "extra", {}).get("category", "unknown"),
                "user_id": getattr(record, "extra", {}).get("user_id", None),
                "role": getattr(record, "extra", {}).get("role", None),
                "ip_address": getattr(record, "extra", {}).get("ip_address", None),
                "details": getattr(record, "extra", {}).get("details", {})
            }
            # Envoyer à Elasticsearch
            if self.es:
                self.es.index(index=self.index, body=log_entry)
            # Envoyer à Logstash
            if self.sock:
                self.sock.sendall(f"{json.dumps(log_entry)}\n".encode('utf-8'))
        except Exception as e:
            self.handleError(record)

    def close(self):
        try:
            if self.sock:
                self.sock.close()
            if self.es:
                self.es.close()
        except Exception as e:
            logging.error(f"Error closing ElasticsearchHandler: {e}")
        super().close()