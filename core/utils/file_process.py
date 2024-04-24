import shutil
import tempfile
from pathlib import Path
from moviepy.editor import *
import logging
import glob

TEMP_DIRECTORY_PATH = os.path.join(tempfile.gettempdir(), 'seeming')
TEMP_OUTPUT_VIDEO_NAME = 'temp.mp4'
logger = logging.getLogger()


def get_temp_frame_paths(target_path):

    "获取当前路径相关的临时文件目录下"

    temp_frames_pattern = get_temp_frames_pattern(target_path, '*')
    return sorted(glob.glob(temp_frames_pattern))


def get_temp_frames_pattern(target_path, temp_frame_prefix):

    "获取当前路径相关的临时文件目录下 所有frame路径"
    temp_directory_path = get_temp_directory_path(target_path)
    if not os.path.exists(temp_directory_path):
        os.makedirs(temp_directory_path)
    return os.path.join(temp_directory_path, temp_frame_prefix + '.jpg')


def get_temp_directory_path(target_path) :

    "获取当前路径相关的临时文件目录下 所有frame路径"
    target_name, _ = os.path.splitext(os.path.basename(target_path))
    return os.path.join(TEMP_DIRECTORY_PATH, target_name)


def get_temp_output_video_path(target_path, name):

    "临时视频路径"

    temp_directory_path = get_temp_directory_path(target_path)
    return os.path.join(temp_directory_path, name)


def create_temp(target_path) :

    "创建临时文件夹"

    temp_directory_path = get_temp_directory_path(target_path)
    Path(temp_directory_path).mkdir(parents = True, exist_ok = True)
    return temp_directory_path


def move_temp(target_path, output_path) :

    "移动文件"
    shutil.move(target_path, output_path)


def clear_temp(target_path):

    "删除临时文件夹"
    if '_' in target_path:
        name = os.path.basename(target_path)
        dic_path = os.path.dirname(target_path)
        target_path = os.path.join(dic_path, name.split('_')[-1])
    temp_directory_path = get_temp_directory_path(target_path)
    parent_directory_path = os.path.dirname(temp_directory_path)
    shutil.rmtree(temp_directory_path)
    if os.path.exists(parent_directory_path) and not os.listdir(parent_directory_path):
        os.rmdir(parent_directory_path)



