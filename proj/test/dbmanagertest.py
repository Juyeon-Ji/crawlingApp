import unittest
import sys
import os

from pymongo import MongoClient
from pymongo.database import Database, Collection

baseprojectpath = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)) 
            )
baseprojectpathexists = False
for syspath in sys.path:
    if baseprojectpath == syspath :
        baseprojectpathexists = True
        break

if not baseprojectpathexists :
    sys.path.append(baseprojectpath)

HOST = "mongodb://192.168.137.223:27017/"
class DatabseManagerTest(unittest.TestCase):
    def setUp(self):
        self.client : MongoClient = MongoClient(HOST)

        self._db : Database = self.client.pymongo_db_test

        self._col : Collection = self._db.test

        self._col1 : Collection = self._db.test2

    def tearDown(self):
        self.client.drop_database("pymongo_db_test")
        pass
        
    def fix_rows(self):
        rows = [{'id':1, 'name':'John'}, 
                {'id':2, 'name':'Jane'},]

        return rows

    def test_insert_1(self):
        rows = self.fix_rows()
        x = self._col.insert_many(rows)

        self.assertTrue(x.acknowledged)

    def test_insert_another_1(self):
        rows = self.fix_rows()
        x = self._col1.insert_many(rows)

        self.assertTrue(x.acknowledged)
        
    # def test_find_value_2(self):
    #     findItem = self._col.find_one()

    #     self.assertEqual(findItem['name'], 'John')
        
    # def test_find_value_another_2(self):
    #     findItem = self._col1.find_one()

    #     self.assertEqual(findItem['name'], 'John')

if __name__ == '__main__':
    unittest.main()