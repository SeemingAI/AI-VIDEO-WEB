from pathlib import Path
import requests
from contextlib import closing
import os
from .file_process import create_temp
from urllib.parse import urlparse
import filetype

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

def is_file(file_path):
	return bool(file_path and os.path.isfile(file_path))


def is_directory(directory_path) :
	return bool(directory_path and os.path.isdir(directory_path))

def is_image(image_path):
	if is_file(image_path):
		return filetype.helpers.is_image(image_path)
	return False


def are_images(image_paths):
	if image_paths:
		return all(is_image(image_path) for image_path in image_paths)
	return False


def is_video(video_path):
	if is_file(video_path):
		return filetype.helpers.is_video(video_path)
	return False

def list_directory(directory_path):
	if is_directory(directory_path):
		files = os.listdir(directory_path)
		return [ Path(file).stem for file in files if not Path(file).stem.startswith(('.', '__')) ]
	return None


def input_file(video_path):
    """
           判断输入路径是本地还是url链接，如果是url下载到临时目录

           input:
           video_path (String): 输入路径

           return:
            video_path (String): 输出路径

       """

    if os.path.exists(video_path):
        return video_path
    elif bool(urlparse(video_path).scheme):
        video_path = download_file(video_path)
        return video_path
    else:
        raise ValueError('请输入本地视频或者视频网址')



