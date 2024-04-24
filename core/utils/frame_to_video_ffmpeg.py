import subprocess
from .file_process import *
from .image_process import arr2pil, image2pil
from .tools import split_filename,are_images
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




def extract_frames(target_path, video_resolution, video_fps):
    """
        使用ffmpeg抽取视频帧到temp文件夹中

        input:
        target_path (String): 视频路径
        video_resolution (String): 视频的分辨率 e.g. 720x1080
        video_fps (int): fps
    """
    temp_frames_pattern = get_temp_frames_pattern(target_path, '%04d')
    for root, dirs, files in os.walk(os.path.dirname(temp_frames_pattern)):
        for file in files:
            # 检查文件名是否以指定的扩展名结尾
            if file.endswith('.jpg'):
                # 构建要删除的文件的完整路径
                file_path = os.path.join(root, file)
                # 删除文件
                os.remove(file_path)
    commands = ['-hwaccel', 'auto', '-i', target_path, '-pix_fmt', 'rgb24']
    commands.extend(['-vf', 'scale=' + str(video_resolution) + ',fps=' + str(video_fps)])
    commands.extend(['-vsync', '0', temp_frames_pattern])
    return run_ffmpeg(commands)




def merge_video(target_path, video_resolution, video_fps, name):
    """
        使用ffmpeg合并视频帧为video并存储到temp文件

        input:
        target_path (String): 输入视频路径
        video_resolution (String): 视频的分辨率 e.g. 720x1080
        video_fps (int): fps
        name (String): Video's name

        return:
        temp_output_video_path (String): Video's path
    """

    temp_output_video_path = get_temp_output_video_path(target_path, name)
    temp_frames_pattern = get_temp_frames_pattern(target_path, '%04d')
    commands = ['-hwaccel', 'auto', '-r', str(video_fps), '-i', temp_frames_pattern, '-c:v', 'libx264']
    commands.extend(['-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-y', temp_output_video_path])
    commands.extend(['-vf', 'scale=' + str(video_resolution) + ',fps=' + str(video_fps)])
    run_ffmpeg(commands)
    return temp_output_video_path, run_ffmpeg(commands)


def np_to_mp4(target_path, data, fps, keep_frames = False):
    """
        np list或者array转为.mp4视频

        input:
        target_path  (String) : 视频输出路径
        data (Numpy List/Numpy array) : 模型输入数据
        fps (Integer) : 帧率
        keep_frames  (bool) : 是否需要存储视频帧

        return:
        temp_output_video_path (String): Video's path
    """

    if  keep_frames:
        temp_directory_path = create_temp(target_path)
        _, name, _ = split_filename(target_path)
        if isinstance(data, list):
            for i in range(len(data)):
                image = arr2pil(data[i])
                image.save(os.path.join(temp_directory_path, '%04d.jpg' % i))
        elif isinstance(data, np.ndarray):
            for i in range(data.shape[0]):
                image = arr2pil(data[i])
                image.save(os.path.join(temp_directory_path, '%04d.jpg' % i))

        image = image2pil(os.path.join(temp_directory_path, '0000.jpg'))
        w, h = image.size
        video_resolution = str(w) + 'x' + str(h)

        temp_output_video_path, flag = merge_video(target_path, video_resolution, fps, name)
        if temp_output_video_path != target_path and flag:
            move_temp(temp_output_video_path, target_path)
            # clear_temp(temp_directory_path)

    else:
        imageio.mimsave(target_path, data, fps= fps)


def compress_image(target_path, output_path, output_image_quality):
	output_image_compression = round(31 - (output_image_quality * 0.31))
	commands = [ '-hwaccel', 'auto', '-i', target_path, '-q:v', str(output_image_compression), '-y', output_path ]
	return run_ffmpeg(commands)

def restore_audio(target_path, output_path, name) :
	temp_output_video_path = get_temp_output_video_path(target_path, name)
	commands = [ '-hwaccel', 'auto', '-i', temp_output_video_path ]
	commands.extend([ '-i', target_path, '-c', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-shortest', '-y', output_path ])
	return run_ffmpeg(commands)