import os
import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

# Variables d'environnement
MONGO_URL = os.getenv("MONGO_URL","mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "bigdefend_logs")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "logs")

client = None
collection = None

def init_mongo():
    global client, collection
    if not MONGO_URL:
        print("❌ MONGO_URL non défini dans .env")
        return
    try:
        # Attendre que MongoDB soit prêt
        time.sleep(5)
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=10000)
        # Vérifier la connexion
        client.admin.command('ping')
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        # Vérifier ou créer la collection
        collections = db.list_collection_names()
        if MONGO_COLLECTION_NAME not in collections:
            db.create_collection(MONGO_COLLECTION_NAME)
            print(f"✅ Collection {MONGO_COLLECTION_NAME} créée")
        print(f"✅ MongoDB connecté à {MONGO_URL}, base: {MONGO_DB_NAME}, collection: {MONGO_COLLECTION_NAME}")
        print(f"Collections disponibles : {collections}")
    except ServerSelectionTimeoutError as e:
        print(f"❌ Échec connexion MongoDB (timeout): {e}")
        collection = None
    except OperationFailure as e:
        print(f"❌ Échec authentification MongoDB: {e}")
        collection = None
    except Exception as e:
        print(f"❌ Erreur inattendue MongoDB: {e}")
        collection = None

# Initialiser la connexion
init_mongo()