from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from config import settings


class MongoDBConnector:
    """singleton class for mongo db connector"""

    _instance: MongoClient = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.MONGO_DB_HOST)
            except ConnectionFailure as e:
                print(f"Error connecting to MongoDB: for QUEUE{e}")
                raise e
        print(f"connected to database uri:{settings.MONGO_DB_HOST}")
        return cls._instance

    def get_database(self):
        return self._instance[settings.MONGO_DB_NAME]

    def close(self):
        if self._instance is not None:
            self._instance.close()
            print("MongoDB connection closed for Queue feature.")
