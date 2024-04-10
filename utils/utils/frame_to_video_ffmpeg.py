import subprocess
import logging
from utils.utils.file_process import *
from utils.utils.image_process import arr2pil, image2pil
from utils.utils.tools import split_filename
import numpy as np

"""
    使用ffmpeg执行视频处理操作

    input:
    args (List): 命令参数
"""


def run_ffmpeg(args):
    commands = ['ffmpeg', '-hide_banner', '-loglevel', 'error']
    commands.extend(args)
    try:
        result = subprocess.run(commands, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as exception:
        logger.debug(exception.stderr.decode().strip(), __name__.upper())
        return False


"""
    使用ffmpeg抽取视频帧到temp文件夹中

    input:
    target_path (String): 视频路径
    video_resolution (String): 视频的分辨率 e.g. 720x1080 
    video_fps (int): fps 
"""


def extract_frames(target_path, video_resolution, video_fps):
    temp_frames_pattern = get_temp_frames_pattern(target_path, '%04d')
    commands = ['-hwaccel', 'auto', '-i', target_path, '-pix_fmt', 'rgb24']
    commands.extend(['-vf', 'scale=' + str(video_resolution) + ',fps=' + str(video_fps)])
    commands.extend(['-vsync', '0', temp_frames_pattern])
    return run_ffmpeg(commands)


"""
    使用ffmpeg合并视频帧为video并存储到temp文件

    input:
    target_path (String): 视频路径
    video_resolution (String): 视频的分辨率 e.g. 720x1080 
    video_fps (int): fps 
    name (String): Video's name

    return:
    temp_output_video_path (String): Video's path
"""


def merge_video(target_path, video_resolution, video_fps, name):

    temp_directory_path, _, _ = split_filename(target_path)
    if not os.path.exists(temp_directory_path):
        temp_output_video_path = get_temp_output_video_path(target_path, name)
        temp_frames_pattern = get_temp_frames_pattern(target_path, '%04d')
    else:
        temp_output_video_path = target_path
        temp_frames_pattern = get_temp_frames_pattern(temp_directory_path, '%04d')
    commands = ['-hwaccel', 'auto', '-r', str(video_fps), '-i', temp_frames_pattern, '-c:v', 'libx264']
    commands.extend(['-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-y', temp_output_video_path])
    commands.extend(['-vf', 'scale=' + str(video_resolution) + ',fps=' + str(video_fps)])
    run_ffmpeg(commands)
    return temp_output_video_path

"""
    np list或者array转为.mp4视频

    input:
    target_path  (String) : 视频输出路径
    data (Numpy List/Numpy array) : 模型输入数据
    keep_frames  (bool) : 是否需要存储视频帧

    return:
    temp_output_video_path (String): Video's path
"""
def np_to_mp4(target_path, np_array, fps, keep_frames = False):

    if  keep_frames:
        temp_directory_path, name, _ = split_filename(target_path)
        if isinstance(np_array, list):
            for i in range(len(np_array)):
                image = arr2pil(np_array[i])
                image.save(os.path.join(temp_directory_path, '%04d.jpg' % i))
        elif isinstance(np_array, np.ndarray):
            for i in range(np_array.shape[0]):
                image = arr2pil(np_array[i])
                image.save(os.path.join(temp_directory_path, '%04d.jpg' % i))

        image = image2pil(os.path.join(temp_directory_path, '0000.jpg'))
        w, h = image.size
        video_resolution = str(w) + 'x' + str(h)
        merge_video(target_path, video_resolution, fps, name)

    else:
        imageio.mimsave(target_path, np_array, fps= fps)