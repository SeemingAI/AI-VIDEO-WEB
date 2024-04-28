# AI生成相关接口文档-个人版

## 调用视频生成AI模型
```
请求中图片和视频地址都是本地路径，可以直接获取文件；
生成的文件要放在 dist_dir 对应的文件夹下面。
回调接口的图片和视频url只包含文件名，不需要目录路径。
```

### 文字转视频|图片转视频|视频转视频
```
POST /api/ai/creation
Content-Type application/json

request: {
    task_id:999,     //请求模型AI的任务id，生成结束后回调golang后端时送上
    category:1,      //1=文字转视频（提示词必填） 2=图片转视频(图片必填) 3=视频转视频(视频必填，提示词可空)
    image_url:"",    //图片文件地址 category=2时必填
    prompt_cn:"",    //中文提示词 category=1时必填
    prompt_en:"",    //英文提示词--已废弃
    ng_prompt_cn:"", //中文负面提示词 可空
    ng_prompt_en:"", //英文负面提示词--已废弃
    fps:24,          //每秒帧数 8-24
    movement:0,      //动作强度 0-4
    guidance:0,      //指导比例 8-24 
    camera:"",       //相机运动
    video_url:"",    //视频文件 cateogry=3时必填
    aspect_ratio:"", //宽高比,可空
    seed:0,          //随机种子
    video_style:0    //视频风格(视频转视频时有效) 0=默认 1=动漫 2=像素
    dist_dir:""      //生成视频要存放的目标文件夹
}

response: {
    err_code:0,   //接口调用结果  0=成功 -1=失败
    err_msg:""    //成功时=空字符 失败时=原因描述
}
```

### 脸部优化
```
POST /api/ai/facefusion
Content-Type application/json

request: {
    task_id:999,        //请求模型AI的任务id，生成结束后回调golang后端时送上
    programe:0,         //0=预览帧 1=生成
    source_file:"",     //图片文件链接
    target_file:"",     //视频文件链接
    frame_number:0,     //预览帧时的帧数编号 programe=0时有效
    reference_face_position:0,   //programe=0时返回的reference_images序号，第1次预览时=0
    reference_face_distance:0.5, //参考强度 0-1.5
    face_selector_mode:"",       //选择模式
    face_analyse_order:"",       //分析顺序
    face_analyse_age:"",         //分析年龄
    face_analyse_gender:"",      //分析性别
    dist_dir:""                  //生成视频要存放的目标文件夹
}

response: {
    err_code:0,         //接口调用结果  0=成功 -1=失败
    err_msg:""          //成功时=空字符 失败时=原因描述
}
```

### 帧率提高
```
POST /api/ai/interpo
Content-Type application/json

request: {
    task_id:999,        //请求模型AI的任务id，生成结束后回调golang后端时送上
    video_url:"",       //视频文件链接
    rate:0,             //提高倍数  2|4|6|8
    dist_dir:""         //生成视频要存放的目标文件夹
}

response:{
    err_code:0,         //接口调用结果  0=成功 -1=失败
    err_msg:""          //成功时=空字符 失败时=原因描述
}
```

### 画质修复
```
POST /api/ai/upscale
Content-Type application/json

request: {
    task_id:999,     //请求模型AI的任务id，生成结束后回调golang后端时送上
    video_url:"",    //视频文件链接
    ratio:0,         //放大比例 1-4
    dist_dir:""      //生成视频要存放的目标文件夹
}

response:{
    err_code:0,         //接口调用结果  0=成功 -1=失败
    err_msg:""          //成功时=空字符 失败时=原因描述
}
```

## 回调golang后端通知结果
```
POST /api/ai/notify
Content-Type application/json

request: {
    task_id:999,            //请求AI模型接口时送上的任务id
    preview_image:"",       //programe=0时，预览帧图片文件(不需要包含路径，只要xxx.jpg即可)
    reference_images:[],    //programe=0时，目标脸部小图文件(不需要包含路径，只要xxx.jpg即可)
    video_url:"",           //生成视频的视频文件名(不需要包含路径，只要xxx.mp4即可)
    err_code:0,             //生成结果 0=成功 -1=失败
    err_msg:""              //成功时=空字符 失败时=原因描述
}

response: {
    err_code:0  //接口调用结果  0=成功 -1=失败
    err_msg:""  //成功时=空字符 失败时=原因描述
}
```