import torch
import uuid
from diffusers import AnimateDiffVideoToVideoPipeline, DDIMScheduler, MotionAdapter
from utils.moudel_utils.interpolation.ema.interp_ema import *
from Obtain_Path import obtain_path
from utils.small_tools.load_video import load_video
from utils.small_tools.vision_resieze import video_resieze
from Translate.zh_en import translation

def video2video_moudel(inference_data,requests_data):
    """
    input:
    inference_data(dic): 推理所需要的数据
    requests_data(dic): 原始相应数据


    output:
    requests_data(dic): 处理好的响应数据
    """


    #尝试加载视频转视频模型，加载模型失败则制作失败的相应数据并返回
    try:
        adapter = MotionAdapter.from_pretrained(obtain_path() +"/moudel_fuction/moudel_reference_fuction/video_video/animatediff-motion-adapter-v1-5-2", torch_dtype=torch.float16)
        video2video = AnimateDiffVideoToVideoPipeline.from_pretrained(obtain_path() +"/moudel_fuction/moudel_reference_fuction/video_video/Realistic_Vision_V5.1_noVAE", motion_adapter=adapter, torch_dtype=torch.float16).to("cuda")
        scheduler = DDIMScheduler.from_pretrained(
            obtain_path() +"/moudel_fuction/moudel_reference_fuction/video_video/Realistic_Vision_V5.1_noVAE",
            subfolder="scheduler",
            clip_sample=False,
            timestep_spacing="linspace",
            beta_schedule="linear",
            steps_offset=1,
        )
        #卸载cpu进行加速
        video2video.enable_model_cpu_offload()
        #切片注意力减少占用
        video2video.enable_vae_slicing()
    except Exception as e:
        requests_data["err_code"] = -1
        requests_data["err_msg"] = str("加载视频转视频模型失败，请下载对应的模型")
        return requests_data
    #根据当前时间生成uuid
    uuid_ = str(uuid.uuid4())
    #组装成文件名
    name = uuid_+ ".mp4"
    #尝试加载数据，加载数据失败则制作失败的相应数据并返回
    try:
        video = load_video(inference_data["video_url"])
        video,width,height = video_resieze(video)
    except:
        requests_data["err_code"] = -1
        requests_data["err_msg"] = str("加载视频失败")
        return requests_data
    #读取推理数据制造随机种子
    generator = torch.manual_seed(inference_data["seed"])
    #检测负面词是否存在后，将推理数据传入文字转图像模型对应的参数接口进行训练，并返回生成数据
    #假如超出显存则，制作失败的相应数据并返回
    try:
        if inference_data["ng_prompt_cn"]=="":
            frames = video2video(
                video=video,
                width=width,
                height=height,
                prompt=translation(inference_data["prompt_cn"]),
                guidance_scale=7.5,
                num_inference_steps=25,
                strength=0.5,
                generator=generator,
            ).frames[0]
        else:
            frames = video2video(
                video=video,
                width=width,
                height=height,
                prompt=translation(inference_data["prompt_cn"]),
                negative_prompt=translation(inference_data["ng_prompt_cn"]),
                guidance_scale=7.5,
                num_inference_steps=25,
                strength=0.5,
                generator=generator,
            ).frames[0]
    except Exception as e:
        requests_data["task_id"] = inference_data["task_id"]
        requests_data["err_code"] = -1
        requests_data["err_msg"] = "上传文件过大"
    path = inference_data["dist_dir"] + "/" + name
    #传入，路径，生成数据，帧率，将np.arrrlist数据转换为视频
    np_to_mp4(path,frames,6)
    #加载帧率提高模型
    model = interpolation_model_load( device=0, model_path = resolve_relative_path('moudel_utils/interpolation/ema/model/ckpt/ours_t.pkl'))
    #将视频路径传入帧率提高模型，提高视频帧率
    interpolation(path, inference_data["dist_dir"],model, rate=4)
    #清除显卡占用
    torch.cuda.empty_cache()
    #制作响应数据
    requests_data["task_id"] = inference_data["task_id"]
    requests_data["video_url"] = name
    return requests_data