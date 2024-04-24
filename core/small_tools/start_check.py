from database.SQLiteDB import SQLiteDB
from core.small_tools.time_query_conversion import time_query_conversion
async def Start_check():
    sq_service = SQLiteDB()
    await sq_service.connect()
    result = await sq_service.Minimum_query_time_in_Main_table()
    if result != None:
        if (result[1] + 300) < time_query_conversion():
            await sq_service.Delete_query_time_in_Table(result[0], result[1])
            await sq_service.close()
            await Start_check()