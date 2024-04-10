from datetime import datetime
#获取当前时间并转换为int值
def time_query_conversion():
    now = datetime.now()
    timestamp = int(now.timestamp())
    return timestamp