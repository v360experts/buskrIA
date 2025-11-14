from pymongo import MongoClient
from pymongo.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

_client: MongoClient = None
_database: Database = None


def get_database() -> Database:
    """Obtener instancia de la base de datos MongoDB"""
    global _database
    if _database is None:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "supermarket_db")
        
        client = MongoClient(mongodb_uri)
        _database = client[db_name]
    
    return _database


def close_database():
    """Cerrar conexión a la base de datos"""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None

