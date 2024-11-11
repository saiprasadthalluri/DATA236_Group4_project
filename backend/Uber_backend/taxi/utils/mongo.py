from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi_booking_db']

def insert_log(collection_name, log_data):
    collection = db[collection_name]
    collection.insert_one(log_data)

def log_ride(ride_data):
    db['ride_logs'].insert_one(ride_data)