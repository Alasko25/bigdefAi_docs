# app/logging/log_setup.py

import logging
from app.logging.mongodb_logger import MongoDBHandler
from app.logging.elasticsearch_logger import ElasticsearchHandler

def setup_logging():
    logger = logging.getLogger("big_defend_ai")
    logger.setLevel(logging.INFO)

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Handler Elasticsearch
    es_handler = ElasticsearchHandler()
    es_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    es_handler.setFormatter(es_formatter)
    logger.addHandler(es_handler)

    # MongoDB
    mongo_handler = MongoDBHandler()
    mongo_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    logger.addHandler(mongo_handler)

    return logger

# Initialise le logger global
logger = setup_logging()
