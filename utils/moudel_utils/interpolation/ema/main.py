import traceback
from utils.utils.file_process import resolve_relative_path
from utils.moudel_utils.interpolation.ema.interp_ema import interpolation, interpolation_model_load


def interpolation_ema_api(info, res_json):

    """
    插帧

    input:
    info (Json): 结构体
        example:
        {
          "task_id" (Int): 任务ID,
          "dist_dir" (String): 输出目录，
          "video_url" (String): 输出路径,
          "rate" (Int): 提高倍数
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
        model = interpolation_model_load(device=0, model_path=
        resolve_relative_path('moudel_utils/interpolation/ema/model/ckpt/ours_t.pkl'))

        video_path = resolve_relative_path(info['video_url'])
        print(video_path)
        output_dir = info['dist_dir']
        rate = info['rate']

        "插帧"
        interp_video_path = interpolation(video_path, output_dir, model, rate=rate)

        return interp_video_path


    except Exception as e:

        traceback.print_exc()

        return -1

if __name__ == "__main__":

    """
    Test example
    """

    info = {
        "task_id": 224,
        "dist_dir" : "/temp/seeming/",
        "video_url": "/root/2d95e65d4dcbfb2823fcf8940fa4d4db.mp4",
        "rate": 3
    }
    res_json = {
        "task_id": int,
        "video_url": "",
        "err_code": int,
        "err_msg": "",
    }

    res = interpolation_ema_api(info, res_json)
    print(res)
