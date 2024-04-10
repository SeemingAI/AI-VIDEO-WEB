import os
def obtain_path():
    #获取当前文件绝对路径
    current_file_path = os.path.abspath(__file__)
    # 分离路径和文件名
    current_directory = os.path.dirname(current_file_path)
    return current_directory