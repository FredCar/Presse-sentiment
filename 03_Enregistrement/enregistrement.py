from pymongo import MongoClient

host = "localhost"
port = 27017
base = "test_presse"
collec = "test"

client = MongoClient(host, port)
db = client[base]

db[collec].insert_many()
