from web_fuction.client_fuction.Model_thread_pool import run_model
from moudel_fuction.moudel_reference_fuction.image_video.image_to_video_fuction import image2video_model
from moudel_fuction.moudel_reference_fuction.text_image.text_to_image_fuction import text_to_image_moudel
from moudel_fuction.moudel_reference_fuction.video_video.video_to_video import video2video_moudel
async def moudel_selection_startup(task_type,inference_data,requests_data):
    """
    input:
    task_type(str): 任务类型
    inference_data(dict): 推理数据
    requests_data（dict）  原始请求数据


    output:
    requests_data(dic): 处理好的请求数据
    """

    # 根据任务类型处理来接受推理数据，并运行模型，处理请求相应数据
    if task_type == "/api/ai/creation":
        if inference_data["category"] == 1:
            requests_data = await run_model(text_to_image_moudel, inference_data, requests_data)
        if inference_data["category"] == 2:
            requests_data = await run_model(image2video_model,inference_data,requests_data)
        if inference_data["category"] == 3:
            requests_data = await run_model(video2video_moudel, inference_data, requests_data)

    return requests_data