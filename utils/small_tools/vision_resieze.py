from PIL import Image

#将图片缩放为h*w约等于num大小的图片
def image_resieze(image):
    num = 1024 * 576
    width, height = image.size
    mul = ((num / (width * height)) ** 0.5)
    width = width * mul
    width = int((width // 64) * 64)
    height = height * mul
    height = int((height // 64) * 64)
    image = image.resize((width, height))
    return width,height,image
#将视频帧缩放为h*w约等于num大小，并将其帧率修改为原来的四分一
def video_resieze(vid):
    images = []
    num = 1024 * 576
    i=0
    print(len(vid))
    for frame in vid:
        if i%4==0:
            image = Image.fromarray(frame)
            width, height = image.size
            mul = ((num / (width * height)) ** 0.5)
            width = width * mul
            width = int((width // 64) * 64)
            height = height * mul
            height = int((height // 64) * 64)
            image = image.resize((width, height))
            images.append(image)
    return images,width,height