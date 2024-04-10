from web_fuction.server_fuction.request_detection import request_detection
import aiohttp
image_to_video_list = []
#采用类视图来处理请求方法和所需要的依赖项
class Generate_post:
    def __init__(self,task_type):
        self.task_type = task_type
    async def __call__(self, request):
        #接受监听数据
        request_data = await request.json()
        print(request_data)
        #处理请求数据并制作响应数据
        response = await request_detection(request_data,self.task_type)
        #发送响应数据
        return aiohttp.web.json_response(response)