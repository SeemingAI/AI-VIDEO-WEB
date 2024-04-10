from web_fuction.client_fuction.moudel_selection_startup import moudel_selection_startup



async def Production_request(task_type,inference_data):

    """
    input:
    task_type(str): 任务类型
    inference_data(dict): 推理数据


    output:
    requests_data(dic): 处理好的请求数据
    """
    #原始请求数据
    requests_data = {
        "task_id":99,
        "preview_image":"",
        "reference_images":[],
        "video_url":"",
        "err_code":0,
        "err_msg":""
    }
    try:
        #选择模型进行推理并制作并处理请求数据
        requests_data = await moudel_selection_startup(task_type,inference_data,requests_data)
    except Exception as e:
        print(e)
    return requests_data
