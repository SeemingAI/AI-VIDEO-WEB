import asyncio
import subprocess
from Obtain_Path import obtain_path
from web_fuction.client_fuction.Generate_client import generate_client
from web_fuction.server_fuction.Generate_server import generate_server
from core.small_tools.start_check import Start_check


run_server = generate_server()
run_client = generate_client()

async def main():
        server_task = asyncio.create_task(run_server())
        client_task = asyncio.create_task(run_client())
        await asyncio.gather(server_task, client_task)





# subprocess.run([binary_path])
#启动前数据库检测
asyncio.run(Start_check())
#启动服务
asyncio.run(main())

