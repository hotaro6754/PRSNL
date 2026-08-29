from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client.cyberos
db.cases.update_many({}, {"$rename": {"updated_at": "last_updated"}})
print('Done')
