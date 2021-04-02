from enum import Enum, auto
from pymongo import MongoClient
from pymongo.database import Database, Collection

HOST = 'mongodb://192.168.137.223:27017/'

class TableType(Enum):
    Category = auto()
    Detail = auto()

class DatabseManager:
    def __init__(self):
        self.client : MongoClient = None
        self._db    : Database = None
        self._col_category   : Collection = None
        self._col_detail : Collection = None

        self.isConnect :bool = False

        self._connect()
        
    def _connect(self):
        self.client = MongoClient(HOST)

        if self.client is not None:
            self.isConnect = True

            self._db            = self.client.pymongo_db # db name
            self._col_category  = self._db.category # table name
            self._col_detail    = self._db.detail   # table name

    def close(self):
        if self.client is not None:
            self.client.close()

    def insert_many(self, value):
        if self.isConnect:
            x = self._col.insert_many(value)

            return x.acknowledged
