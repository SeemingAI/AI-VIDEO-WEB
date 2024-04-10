from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
from Obtain_Path import obtain_path
import torch
import uuid
from utils.small_tools.vision_resieze import image_resieze
from utils.utils.frame_to_video_ffmpeg import np_to_mp4
from utils.moudel_utils.interpolation.ema.interp_ema import *
#加载以及使用图像转模型数据，以及处理response数据
def image2video_model(inference_data,requests_data):
    """
    input:
    inference_data(dic): 推理所需要的数据
    requests_data(dic): 原始相应数据


    output:
    requests_data(dic): 处理好的响应数据
    """


    #尝试加载图像转视频模型，加载模型失败则制作失败的相应数据并返回
    try:
        image2video = StableVideoDiffusionPipeline.from_pretrained(
            obtain_path()+"/moudel_fuction/moudel_reference_fuction/image_video/svd/stable-video-diffusion-img2vid-xt-1-1", torch_dtype=torch.float16, variant="fp16"
            )
    except Exception as e:
        requests_data["err_code"] = -1
        requests_data["err_msg"] = str("加载图片转视频模型失败，请下载对应的模型")
        return requests_data
    #卸载cpu到gpu便于加速
    image2video.enable_model_cpu_offload()
    #根据当前时间生成uuid
    uuid_ = str(uuid.uuid4())
    #组装成文件名
    name = uuid_+ ".mp4"
    #尝试加载数据，加载数据失败则制作失败的相应数据并返回
    try:
        image = load_image(inference_data["image_url"])
    except:
        requests_data["err_code"] = -1
        requests_data["err_msg"] = str("加载图片失败")
        return requests_data
    #修改图像尺寸
    width, height , image = image_resieze(image)
    #读取推理数据制造随机种子
    generator = torch.manual_seed(inference_data["seed"])
    #将推理数据传入模型参数接口进行训练，并返回生成数据
    frames = image2video(image, width=width, height=height, decode_chunk_size=8, fps=inference_data["fps"]//4, min_guidance_scale=2.5, max_guidance_scale=3,
         motion_bucket_id=120+60*inference_data["movement"], generator=generator, num_frames=24).frames[0]
    #拼接生成数据路径
    path = inference_data["dist_dir"]+"/"+name
    #传入，路径，生成数据，帧率，将np.arrrlist数据转换为视频
    np_to_mp4(path,frames,6)
    #加载帧率提高模型
    model = interpolation_model_load( device=0, model_path = resolve_relative_path('moudel_utils/interpolation/ema/model/ckpt/ours_t.pkl'))
    #将视频路径传入帧率提高模型，提高视频帧率
    interpolation(path, inference_data["dist_dir"],model, rate=3)
    #清除显卡占用
    torch.cuda.empty_cache()
    #制作响应数据
    requests_data["task_id"] = inference_data["task_id"]
    requests_data["video_url"] = name
    return requests_data
