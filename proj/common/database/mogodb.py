
from enum import Enum, auto
from pymongo import MongoClient
from pymongo.database import Database, Collection

HOST = 'mongodb://192.168.137.223:27017/'

class TableType(Enum):
    Category = auto()
    Detail = auto()

class MogoDBManager(object):
    def __init__(self):
        self._client : MongoClient = None
        
        self._col_category   : Collection = None
        self._col_detail : Collection = None

        self.isConnect :bool = False

        self._connect()
        
    def _connect(self):
        self._client = MongoClient(HOST)

        if self._client is not None:
            self.isConnect = True

            _db            = self._client.pymongo_db # db name
            self._col_category  = self._db.category # table name
            self._col_detail    = self._db.detail   # table name

    def close(self):
        if self._client is not None:
            self._client.close()

    def insert_many(self, value) -> bool:
        if self.isConnect:
            x = self._col.insert_many(value)

            return x.acknowledged