
from enum import Enum, auto
from pymongo import MongoClient
from pymongo.database import Database, Collection

HOST = 'mongodb://192.168.137.223:27017/'


class TableType(Enum):
    Category = auto()
    Detail = auto()


class MongoDBManager(object):
    host: str
    database: str
    collection: dict

    def __init__(self, host, database, collection):
        self.host = host
        self.database = database
        self.collection = collection

        self._client: MongoClient = None

        self._collection: Collection = None
        self._col_category: Collection = None
        self._col_detail: Collection = None

        self.isConnect: bool = False

        self._connect()
        
    def _connect(self):
        self._client = MongoClient(HOST)

        if self._client is not None:
            self.isConnect = True

            self._db: Database = self._client[self.database]  # db name

            self._col_category = self._db[self.collection.get('table-1')]  # table name
            self._col_detail = self._db[self.collection.get('table-2')]  # table name

    def close(self):
        if self._client is not None:
            self._client.close()

    def insert_one(self, collection: str, value: dict) -> bool:
        if self.isConnect:
            x = self._db[collection].insert_one(value)

            return x.acknowledged

    def insert_many(self, collection: str, value):
        if self.isConnect:

            return self._db[collection].insert_many(value)

    def find_all(self, collection: str):
        if self.isConnect:
            return self._db[collection].find()

