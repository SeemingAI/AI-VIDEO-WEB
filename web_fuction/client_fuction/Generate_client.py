import aiohttp
import asyncio

from database.SQLiteDB import SQLiteDB
from web_fuction.client_fuction.client_messge_check import client_messge_check
from web_fuction.client_fuction.send_request import send_request
from web_fuction.client_fuction.Production_request import Production_request

#
class generate_client():
    async def __call__(self):
        #创建数据库连接实例
        sq_service = SQLiteDB()
        #连接数据库
        await sq_service.connect()
        #创建异步客户端
        async with aiohttp.ClientSession() as session:
            while True:
                    #读取最早进入数据库的数据，如果数据库中不存在数据则返回空值
                    task_type,inference_data = await client_messge_check()
                    #判断数据库中是否有数据
                    if inference_data!=None:
                       #根据任务类型，和推理数据生成请求数据
                       requests_data = await Production_request(task_type,inference_data)
                       #发送请求数据返回相应数据
                       response = await send_request(session,requests_data)
                       print(response)
                       #删除已经处理完的后端请求数据
                       await sq_service.Delete_query_time_in_Table(task_type,inference_data["Establishment_time"])
                    else:
                        await asyncio.sleep(0.01)