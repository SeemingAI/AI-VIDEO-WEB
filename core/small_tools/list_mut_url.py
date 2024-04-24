#将字符串分割转换为列表
def list_to_str(list):
    list_str = ','.join(map(str, list))
    return list_str

def str_to_list(list_str):
    int_list = [float(i) for i in list_str.split(',')]
    return int_list
