

#向指定ip与端口号发送数据并返回响应数据
async def send_request(session,data):
    async with session.post('http://127.0.0.1:8088/api/ai/notify', json=data) as response:
        return await response.json()