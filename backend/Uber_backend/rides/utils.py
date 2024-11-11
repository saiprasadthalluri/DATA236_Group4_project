from taxi.utils.mongo import insert_log

def log_ride(ride_data):
    insert_log('ride_logs', ride_data)
