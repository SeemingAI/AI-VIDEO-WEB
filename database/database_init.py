import asyncio
import aiosqlite

async def database_init():
    try:
        conn = await aiosqlite.connect('task_list.db')
        async with conn.cursor() as cursor:
            await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Main_Table
                (
                    Task_Type          TEXT,
                    Establishment_time INTEGER
                )
                ''' )
            await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS creation
                (
                    Establishment_time INTEGER,
                    task_id      INTEGER,
                    category     INTEGER,
                    image_url    TEXT,
                    prompt_cn    TEXT,
                    prompt_en    TEXT,
                    ng_prompt_cn TEXT,
                    ng_prompt_en TEXT,
                    fps          INTEGER,
                    movement     INTEGER,
                    guidance     INTEGER,
                    camera       TEXT,
                    video_url    TEXT,
                    aspect_ratio TEXT,
                    dist_dir     TEXT,
                    seed         INTEGER
                )
                ''' )
            await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tracking_creation
                (
                    Establishment_time INTEGER,
                    task_id            INTEGER,
                    image_url          TEXT,
                    fps                INTEGER,
                    movement           INTEGER,
                    camera             TEXT,
                    tracking_points    TEXT,
                    dist_dir     TEXT
                )
                ''' )
            await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS facefusion
                (
                    Establishment_time      INTEGER,
                    task_id                 INTEGER,
                    programe                INTEGER,
                    source_file             TEXT,
                    target_file             TEXT,
                    frame_number            INTEGER,
                    reference_face_position INTEGER,
                    reference_face_distance REAL,
                    face_selector_mode      TEXT,
                    face_analyse_order      TEXT,
                    face_analyse_age        TEXT,
                    face_analyse_gender     TEXT,
                    dist_dir                TEXT
                )
                ''' )
            await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interpo
                (
                    Establishment_time      INTEGER,
                    task_id                 INTEGER,
                    video_url               TEXT,
                    rate                    INTEGER,
                    dist_dir                TEXT                  
                )
                ''' )
            await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS upscale
                (
                    Establishment_time      INTEGER,
                    task_id                 INTEGER,
                    video_url               TEXT,
                    ratio                   INTEGER,
                    dist_dir                TEXT                  
                )
                ''' )
            await conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 确保游标和连接都被关闭
        if 'cursor' in locals():
            await cursor.close()
        if 'conn' in locals():
            await conn.close()
