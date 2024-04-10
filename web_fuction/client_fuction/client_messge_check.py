from database.SQLiteDB import SQLiteDB
#检测数据库里面最早的数据，如果存在则返回任务类型和时间标签，和副表数据
async def client_messge_check():
    #创建数据库连接实例
    sq_service = SQLiteDB()
    #连接数据库
    await sq_service.connect()
    #寻早最早进入的数据
    result = await sq_service.Minimum_query_time_in_Main_table()
    if result != None:
        #根据任务与时间标签，取副表素具
        data = await sq_service.Select_query_time_in_Table(result[0], result[1])
        #关闭连接
        await sq_service.close()
        #返回数据
        return result[0],data
    else:
        data = None
    return result, data