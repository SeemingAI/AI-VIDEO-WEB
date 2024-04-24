import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from tqdm import tqdm
from moviepy.editor import *
from core.utils.file_process import get_temp_frame_paths, move_temp
from Obtain_Path import resolve_relative_path
from core.utils.frame_to_video_ffmpeg import extract_frames, merge_video
from core.utils.tools import split_filename


MODELS = \
    {
        'real_esrgan_x2plus':
            {
                'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrgan_x2plus.pth',
                'path': resolve_relative_path(
                    'moudel_fuction/moudel_reference_fuction/frame_enhance/ckpt/real_esrgan_x2plus.pth'),
                'scale': 2
            },
        'real_esrgan_x4plus':
            {
                'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrgan_x4plus.pth',
                'path': resolve_relative_path(
                    'moudel_fuction/moudel_reference_fuction/frame_enhance/ckpt/real_esrgan_x4plus.pth'),
                'scale': 4
            },
        'real_esrnet_x4plus':
            {
                'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrnet_x4plus.pth',
                'path': resolve_relative_path(
                    'moudel_fuction/moudel_reference_fuction/frame_enhance/ckpt/real_esrnet_x4plus.pth'),
                'scale': 4
            }
    }


def blend_frame(temp_vision_frame, paste_vision_frame, blend):
    frame_enhancer_blend = 1 - (blend / 100)
    temp_vision_frame = cv2.resize(temp_vision_frame, (paste_vision_frame.shape[1], paste_vision_frame.shape[0]))
    temp_vision_frame = cv2.addWeighted(temp_vision_frame, frame_enhancer_blend, paste_vision_frame,
                                        1 - frame_enhancer_blend, 0)
    return temp_vision_frame


def get_frame_processor(model_name):
    model = MODELS.get(model_name)
    model_path = model.get('path')
    model_scale = model.get('scale')
    FRAME_PROCESSOR = RealESRGANer(
        model_path=model_path,
        model=RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            scale=model_scale
        ),
        device='cuda:0',
        scale=model_scale
    )
    return FRAME_PROCESSOR


def frame_enhance_realesrgan(target_path, model, output_dir, outscale=1, width=0, height=0):

    """
       画质增强 Realesrgan

       可选模型：real_esrnet_x4plus
               real_esrgan_x4plus
               real_esrgan_x2plus

       Args:
       target_path: 输入视频路径 支持.mp4/gif两种格式
       model: 选择的模型
       output_dir: 输出视频的目录
       outscale: 输出的尺寸为原有的几倍
       width: 指定输出的宽度
       height: 指定输出的高度

       return:
       enhance_video (List): video path

       tips: outscale 和 (width x height) 默认只使用其中一种方式输出特定尺寸视频
       """


    upsampler = get_frame_processor(model)
    output_dir, name, type = split_filename(target_path)

    if target_path.endswith('.mp4'):
        video_path = target_path
        name_mp4 = name
    elif target_path.endswith('.gif'):
        name_mp4 = name.split(".")[0] + '.mp4'
        video_path = os.path.join(output_dir, name_mp4)
        clip = VideoFileClip(target_path, verbose=False)
        clip.write_videofile(video_path, verbose=False)
    video_capture = cv2.VideoCapture(video_path)

    # video infomation
    if video_capture.isOpened():
        video_fps = video_capture.get(cv2.CAP_PROP_FPS)
        video_width = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        video_height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        video_capture.release()
    else:
        raise ValueError('video_open_failed')

    # 输出尺寸
    if width != 0 or height != 0:
        if width != video_width:
            video_width == width
        elif height != video_height:
            video_height == height
        outscale = max(height / video_height, width / video_width)
    video_resolution = '%dx%d' % (video_width, video_height)

    # 逐帧处理
    if extract_frames(video_path, video_resolution, video_fps):
        temp_frame_paths = get_temp_frame_paths(video_path)
    else:
        raise ValueError('extract frames failed!')
    progress = tqdm(total=len(temp_frame_paths), desc='enhancing', unit='frame', ascii=' =')
    for i, img_path in enumerate(temp_frame_paths):
        try:
            img = cv2.imread(img_path, cv2.IMREAD_COLOR)
            enhance, _ = upsampler.enhance(img, outscale=outscale)
            blend = blend_frame(enhance, img, blend=80)
            cv2.imwrite(img_path, blend)
        except RuntimeError as error:
            print('Error', error)
        rate = i * int(video_fps) / len(temp_frame_paths) * 100
        progress.update()
        progress.set_postfix(rate=rate)
    progress.close()

    # 合成视频并输出
    enhance_video, flag = merge_video(video_path, video_resolution, video_fps, name_mp4)
    if flag:
        _, name, _ = split_filename(enhance_video)
        output_path = os.path.join(output_dir,name)
        move_temp(enhance_video,output_path)
        return output_path
    else:
        raise ValueError('Enhance video failed!')


if __name__ == "__main__":

    """
    Test Example
    """

    res = frame_enhance_realesrgan(target_path='/temp/test-many1.mp4',
                                   output_dir= '/temp/seeming/',
                                   model='real_esrgan_x2plus',
                                   outscale=1)
