from aiohttp import web
import aiohttp
import asyncio
from datalorder.load_config import load_config
from web_fuction.server_fuction.Generate_post import Generate_post
#读取config文件中的监听路径数据
post_config = load_config("./config/web_config.ini").items("POST_PATH")
#读取config文件的监听端口数据
port = load_config("./config/web_config.ini").getint("PORT",   "Port")
#创建服务端生成
class generate_server:
    async def __call__(self):
        #创建Application的实例
        app = aiohttp.web.Application()
        #根据读取到的路径列表来监听不同端口
        for i in range(len(post_config)):
            handle_post = Generate_post(post_config[i][1])
            app.add_routes([aiohttp.web.post(post_config[i][1], handle_post,)])
        #启动时间循环
        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        #连接指定ip与端口号的http连接
        site = aiohttp.web.TCPSite(runner, '127.0.0.1', port)
        #启动程序
        await site.start()
        try:
            await asyncio.Future()  # Wait forever
        except asyncio.CancelledError:
            pass
        finally:
            await runner.cleanup()