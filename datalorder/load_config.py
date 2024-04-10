import configparser
#读取config文件
def load_config(config_file):
    """
    input:
    config_file(str): config文件路径

    output:
    config(list): config文件内容（二维列表）
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config