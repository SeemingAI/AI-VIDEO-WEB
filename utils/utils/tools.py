from pathlib import Path
import requests
from contextlib import closing
import os
from utils.utils.file_process import create_temp



def download_file(url):

    """
        根据url下载文件并存储到临时文件夹中

        input:
        url (String): 文件路径

        return:
        local_filename (String): Video's path
        example:/temp/seeming/filename/filename.extension
    """

    try:
        import uuid
        import mimetypes
        response = requests.head(url, timeout=5)

        if response.status_code == 200:
            mime = mimetypes.guess_type(url)[0]
            if mime:
                file_extension = '.' + mime.split('/')[1]
            elif 'content-type' in response.headers:
                import mimetypes
                content_type = response.headers['content-type']
                file_extension = mimetypes.guess_extension(content_type)
            else:
                file_extension = os.path.splitext(url)[-1]
        else:
            raise Exception('response status code')

        var_name = str(uuid.uuid4())[:8] + file_extension
        temp_directory_path = create_temp(var_name)
        local_filename = os.path.join(temp_directory_path, var_name)

        with closing(requests.get(url, stream=True)) as response:
            chunk_size = 1024
            with open(local_filename, "wb") as f:
                for data in response.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    f.flush()
        return local_filename
    except BaseException as e:
        raise ValueError(e)


def split_filename(filename):

    """
        切割文件路径

        input:
        url (String): 文件路径

        return:
        dirname (String): 目录
        basename (String): filename
        extname (String): 扩展

    """

    absname = os.path.abspath(filename)
    dirname, basename = os.path.split(absname)
    split_tmp = basename.rsplit('.', maxsplit=1)
    if len(split_tmp) == 2:
        rootname, extname = split_tmp
    elif len(split_tmp) == 1:
        rootname = split_tmp[0]
        extname = None
    else:
        raise ValueError("programming error!")
    return dirname, basename, extname
