from pymongo import MongoClient
import os

def get_mongo_client(uri=None):
    """Initialize and return a MongoDB client."""
    if uri is None:
        uri = os.getenv("MONGO_URI", "mongodb://admin:password@mongodb:27017/")
    return MongoClient(uri)

def log_query(db, collection_name, log_data):
    """Insert a log entry (e.g., user query, answer, metadata) into MongoDB."""
    collection = db[collection_name]
    collection.insert_one(log_data)

def get_logs(db, collection_name, filter_query=None) :
    """Retrieve logs from MongoDB."""
    collection = db[collection_name]
    if filter_query is None:
        filter_query = {}
    return list(collection.find(filter_query))