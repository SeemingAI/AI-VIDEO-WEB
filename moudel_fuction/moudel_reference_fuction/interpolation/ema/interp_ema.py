from moudel_fuction.moudel_reference_fuction.interpolation.ema.config import config as cfg
from moudel_fuction.moudel_reference_fuction.interpolation.ema.config.interpolation_ema import Model
from moudel_fuction.moudel_reference_fuction.interpolation.ema.config.padder import InputPadder

from core.utils.frame_to_video_ffmpeg import np_to_mp4
from Obtain_Path import resolve_relative_path
from core.utils.file_process import clear_temp
from core.utils.tools import split_filename

from core.utils.tools import input_file

import numpy as np
import os
import torch
import cv2
from pathlib import Path


def interpolation_model_load(device, model_path):

    """
    加载模型参数

    input:
    device (int): cuda number
    model_path (String): 模型路径

    return:
    Tracking_net (List): 模型
    """

    cfg.MODEL_CONFIG['LOGNAME'] = 'ours_t'
    cfg.MODEL_CONFIG['MODEL_ARCH'] = cfg.init_model_config(
        F = 32,
        depth = [2, 2, 2, 4, 4]
    )

    model = Model(-1,device,model_path)
    model.load_model()
    model.eval()

    return model


def interpolation(video_path, output_dir,model, rate, fps=0):

    """
    根据插帧，生成视频

    input:
    video_path (String): local_path/video_url 输入路径
    output_dir (String): 输出的目录
    model (List): 模型
    rate (Int): 插帧的倍数
    fps (Int): 输出的帧率 该值省略的时候，默认帧率也提高rate倍，即保持原视频时长


    return:
    output_path (String): 输出路径
    """

    # 输出路径
    video_path = input_file(video_path)
    # video_path = frame_enhance_realesrgan_x4plus(video_path, outscale=1)
    _, name, _ = split_filename(video_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # video information
    cap = cv2.VideoCapture(video_path)
    input_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # .mp4 => List
    video = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            video.append(frame)
        else:
            cap.release()
            clear_temp(video_path)
            break

    import time
    start_time = time.time()

    images = []

    for frame_number in range(total_frames-1):
        try:
          I0 = video[frame_number]
          I2 = video[frame_number + 1]
          I0_ = (torch.tensor(I0.transpose(2, 0, 1)).cuda() / 255.).unsqueeze(0)
          I2_ = (torch.tensor(I2.transpose(2, 0, 1)).cuda() / 255.).unsqueeze(0)
          padder = InputPadder(I0_.shape, divisor=32)
          I0_, I2_ = padder.pad(I0_, I2_)
          images.append(I0[:, :,::-1])

          if frame_number != total_frames - 2:
              preds = model.multi_inference(I0_, I2_, TTA=False,
                                        time_list=[(i + 1) * (1. / rate) for i in range(rate - 1)],
                                        fast_TTA=False)
              for i, pred in enumerate(preds):
                  images.append(
                  (padder.unpad(pred).detach().cpu().numpy().transpose(1, 2, 0) * 255.0).astype(np.uint8)[:, :, ::-1])
          else:
              preds = model.multi_inference(I0_, I2_, TTA=False,
                                            time_list=[(i + 1) * (1. / ((rate-1)*2)) for i in range((rate-1)*2)],
                                            fast_TTA=False)
              for i, pred in enumerate(preds):
                  images.append(
                      (padder.unpad(pred).detach().cpu().numpy().transpose(1, 2, 0) * 255.0).astype(np.uint8)[:, :,::-1])
              images.append(I2[:, :,::-1])

        except EOFError as e:(
            print('An IOError occurred. {}'.format(e.args[-1])))
    cap.release()


    if fps != 0 :
        output_fps = fps
    else:
        output_fps = input_fps * rate


    output_path = os.path.join(output_dir, name)
    np_to_mp4(output_path, images, fps = output_fps, keep_frames=True)


    cap = cv2.VideoCapture(output_path)
    output_total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    output_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    end_time = time.time()
    print('运行时间:{}, 原始帧数{}, 插帧后的总数{}, 帧率{} '
          .format(end_time - start_time,total_frames,output_total_frames,int(output_fps)))

    print(output_path)
    return output_path




