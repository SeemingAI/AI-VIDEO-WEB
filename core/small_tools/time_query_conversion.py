from datetime import datetime

def time_query_conversion():
    now = datetime.now()
    timestamp = int(now.timestamp())
    return timestamp