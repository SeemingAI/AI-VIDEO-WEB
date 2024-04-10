from database.SQLiteDB import SQLiteDB
async def request_detection(request_data,task_type):
    """
    input:
    request_data请求数据(dic): 请求数据
    task_type(str): 任务类型


    output:
    response(dic): 响应数据
    """
    #创建数据库实例
    sq_service = SQLiteDB()
    #连接数据库
    await sq_service.connect()
    #检测主表长度，如果等待数据过多，则拒绝
    if await sq_service.retrieval_length():
        #根据任务类型将后端请求数据插入数据库
        await sq_service.Insert_table(task_type,request_data)
        response = {
            'err_code': 0,
            "err_msg": ""
        }
    else:
        response = {
            'err_code': 1,
            "err_msg": "计算繁忙"
        }
    #关闭数据库连接
    await sq_service.close()
    return response