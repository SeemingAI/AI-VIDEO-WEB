import aiosqlite
import sqlite3
from utils.small_tools.list_mut_url import list_to_str
from utils.small_tools.time_query_conversion import time_query_conversion


class SQLiteDB(object):
    def __init__(self):
        self.conn = None
    async def connect(self):
        self.conn = await aiosqlite.connect('task_list.db')
    async def close(self):
        if self.conn:
            await self.conn.close()
    #查询表长度是否满足可以进入的条件
    async def retrieval_length(self):
        async with self.conn.cursor() as cursor:
            await cursor.execute('''
            SELECT COUNT(*) FROM Main_Table;
            ''')
            result = await cursor.fetchone()
            await self.conn.commit()
        return result[0]<5
    #向主表中插入数据
    async def Insert_Main_Table(self,task_type,times):
        async with self.conn.cursor() as cursor:
            await cursor.execute("INSERT INTO Main_Table (Task_Type, Establishment_time) "
                                 "VALUES (?, ?)",
                           (task_type, times))
            await self.conn.commit()
    #向运动笔刷表中插入数据
    async def Insert_tracking_creation_Table(self,times,responsedata):
        async with self.conn.cursor() as cursor:
            await cursor.execute("INSERT INTO tracking_creation ( Establishment_time,task_id,image_url,fps,"
                                 "movement,camera,tracking_points,dist_dir) "
                                 "VALUES (?,?,?,?,?,?,?,?)",
                                 (times,responsedata["task_id"],responsedata["image_url"],
                                  responsedata["fps"],responsedata["movement"],responsedata["camera"],
                                  responsedata["tracking_points"],responsedata["dist_dir"]))
            await self.conn.commit()
    #通用视频生成ai表中插入数据
    async def Insert_creation_Table(self,times,responsedata):
        async with self.conn.cursor() as cursor:
            await cursor.execute("INSERT INTO creation ( Establishment_time,task_id,category,image_url,"
                                 "prompt_cn,prompt_en,ng_prompt_cn,ng_prompt_en,fps,movement,"
                                 "guidance,camera,video_url,aspect_ratio,dist_dir,seed)"
                                 "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                (times,responsedata["task_id"],responsedata["category"],
                                 responsedata["image_url"],responsedata["prompt_cn"],responsedata["prompt_en"],
                                 responsedata["ng_prompt_cn"],responsedata["ng_prompt_en"],responsedata["fps"],
                                 responsedata["movement"],responsedata["guidance"],responsedata["camera"],
                                 responsedata["video_url"],responsedata["aspect_ratio"],responsedata["dist_dir"],responsedata["seed"]))
            await self.conn.commit()
    #脸部优化表中插入数据
    async def Insert_facefusion_Table(self,times,responsedata):
        async with self.conn.cursor() as cursor:
            await cursor.execute("INSERT INTO facefusion ( Establishment_time,task_id,programe,source_file,"
                                 "target_file,frame_number,reference_face_position,"
                                 "reference_face_distance,face_selector_mode,face_analyse_order,"
                                 "face_analyse_age,face_analyse_gender,dist_dir) "
                                 "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                (times,responsedata["task_id"],responsedata["programe"],
                                 responsedata["source_file"],responsedata["target_file"],responsedata["frame_number"],
                                 responsedata["reference_face_position"],responsedata["reference_face_distance"],responsedata["face_selector_mode"],
                                 responsedata["face_analyse_order"],responsedata["face_analyse_age"],responsedata["face_analyse_gender"],responsedata["dist_dir"]))
            await self.conn.commit()
    #帧率提高表中插入数据
    async def Insert_interpo_Table(self,times,responsedata):
        async with self.conn.cursor() as cursor:
            await cursor.execute("INSERT INTO interpo ( Establishment_time,task_id,video_url,rate,dist_dir"
                                 " VALUES (?,?,?,?,?)",
                                (times,responsedata["task_id"],responsedata["programe"],
                                 responsedata["video_url"],responsedata["rate"]))
            await self.conn.commit()
    #画质提高表中插入数据
    async def Insert_upscale_Table(self,times,responsedata):
        async with self.conn.cursor() as cursor:
            await cursor.execute("INSERT INTO upscale ( Establishment_time,task_id,video_url,ratio,dist_dir"
                                 " VALUES (?,?,?,?,?)",
                                (times,responsedata["task_id"],responsedata["programe"],
                                 responsedata["video_url"],responsedata["ratio"],responsedata["dist_dir"]))
            await self.conn.commit()
    #服务端插入数据接口
    async def Insert_table(self,task_type,responsedata):
        times = time_query_conversion()
        await self.Insert_Main_Table(task_type,times)
        if(task_type == "/api/ai/creation"):
            await self.Insert_creation_Table(times,responsedata)
        if(task_type == "/api/ai/tracking_creation"):
            responsedata["tracking_points"] = list_to_str(responsedata["tracking_points"])
            await self.Insert_tracking_creation_Table(times,responsedata)
        if(task_type == "/api/ai/facefusion"):
            await self.Insert_facefusion_Table(times,responsedata)
        if(task_type == "/api/ai/interpo"):
            await self.Insert_interpo_Table(times,responsedata)
        if(task_type == "/api/ai/upscale"):
            await self.Insert_upscale_Table(times,responsedata)
    #查询最先进入的数据
    async def Minimum_query_time_in_Main_table(self):
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM Main_Table WHERE Establishment_time = (SELECT MIN(Establishment_time) FROM Main_Table)")
            result = await cursor.fetchone()
            await self.conn.commit()
        return result
    #根据时间戳删除数据
    async def Delete_query_time_in_Table(self,Task_Type,times):
        async with self.conn.cursor() as cursor:
            await cursor.execute("DELETE FROM Main_Table WHERE Establishment_time = ?", (times,))
            await cursor.execute("DELETE FROM" + " " + Task_Type.rsplit('/', 1)[-1]+ " " +"WHERE Establishment_time = ?", (times,))
            result = await cursor.fetchone()
            await self.conn.commit()

        return result
    #根据时间戳和任务类型检索数据
    async def Select_query_time_in_Table(self, Task_Type, times):
        async with self.conn.cursor() as cursor:
            await cursor.execute("PRAGMA table_info" + "(" + Task_Type.rsplit('/', 1)[-1] + ")")
            columns = await cursor.fetchall()
            columns = [info[1] for info in columns]
            await cursor.execute("SELECT * FROM" + " " + Task_Type.rsplit('/', 1)[-1] + " " + "WHERE Establishment_time = ?", (times,))
            result = await cursor.fetchone()
            result = {columns[i]: value for i, value in enumerate(result)}
            await self.conn.commit()
        return result
# async def main():
#     a = SQLiteDB()
#     await a.connect()
#
#     await a.close()

# cursor.execute("INSERT INTO Main_Table (Task_Type, Establishment_time) VALUES (?, ?)", ("/api/ai/creation",time_query_conversion()))
"""插入数据（tracking_creation）"""
# cursor.execute("INSERT INTO tracking_creation (tracking_points) VALUES (?)", (int_list_str,))
# conn.commit()
# cursor.execute('''
# SELECT * FROM Main_Table WHERE Establishment_time = (SELECT MAX(Establishment_time) FROM Main_Table)
# ''')
# max_row = cursor.fetchone()
# print(max_row)