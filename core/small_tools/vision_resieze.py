from PIL import Image


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
def video_resieze(vid):
    i=0
    num_frames = 0
    images = []
    num = 1024 * 576
    for frame in vid:
        if i>120:
            break
        image = Image.fromarray(frame)
        width, height = image.size
        mul = ((num / (width * height)) ** 0.5)
        width = width * mul
        width = int((width // 64) * 64)
        height = height * mul
        height = int((height // 64) * 64)
        image = image.resize((width, height))
        if i % 8 == 0:
            images.append(image)
            num_frames=num_frames+1
        i = i + 1
    return images,width,height,num_frames