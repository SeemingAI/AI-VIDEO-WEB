import traceback
from Obtain_Path import resolve_relative_path
from moudel_fuction.moudel_reference_fuction.frame_enhance.realesrgan_up import frame_enhance_realesrgan

def frame_enhance_realesrgan_api(info, res_json):

    """
    插帧

    input:
    info (Json): 结构体
        example:
        {
          "task_id" (Int): 任务ID,
          "dist_dir" (String): 输出目录，
          "video_url" (String): 输出路径,
          "ratio" (Int): upscale的倍数
    }

    res_json (Json): 结构体
        reponse = {
          "task_id" (Int): ,
          "video_url" (String): ,
          "err_code" (Int): ,
          "err_msg" (String): ,
    }


    return:
    output_path (String): 输出local path

    """

    try:
        "加载interpolation模型"

        video_path = resolve_relative_path(info['video_url'])
        output_dir = info['dist_dir']
        ratio = info['ratio']

        "upscale"
        upscale_video_path = frame_enhance_realesrgan(target_path=video_path,
                                       output_dir=output_dir,
                                       model='real_esrgan_x2plus',
                                       outscale=ratio )

        return upscale_video_path


    except Exception as e:

        traceback.print_exc()

        return -1

if __name__ == "__main__":

    """
    Test example
    """

    info = {
        "task_id": 224,
        "dist_dir" : "E:/test",
        "video_url": "D:/face_test_example/target-test.mp4",
        "ratio": 1
    }
    res_json = {
        "task_id": int,
        "video_url": "",
        "err_code": int,
        "err_msg": "",
    }

    res = frame_enhance_realesrgan_api(info, res_json)
    print(res)

