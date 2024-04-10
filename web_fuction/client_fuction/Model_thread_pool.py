import asyncio
import time
async def run_model(model,inferdata,requestdata):
    loop = asyncio.get_running_loop()
    # 使用线程池执行器来运行同步的模型加载和推理代码
    requestdata = await loop.run_in_executor(None,model, inferdata,requestdata)
    return requestdata
