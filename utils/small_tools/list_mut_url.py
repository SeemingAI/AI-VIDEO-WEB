#将列表分割转换为字符串
def list_to_str(list):
    list_str = ','.join(map(str, list))
    return list_str
#将字符串分割转换为内涵元素类型为float的列表
def str_to_list(list_str):
    int_list = [float(i) for i in list_str.split(',')]
    return int_list
