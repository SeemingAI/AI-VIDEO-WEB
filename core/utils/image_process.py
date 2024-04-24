from PIL import Image
import numpy as np
import os


def image2pil(filename):
    "图像为PIL对象"
    return Image.open(filename)


def image2arr(filename):
    "转换为numpy array"
    pil = image2pil(filename)
    return pil2arr(pil)


def pil2arr(pil):
    "PIL => Numpy array"
    if isinstance(pil, list):
        arr = np.array(
            [np.array(e.convert('RGB').getdata(), dtype=np.uint8).reshape(e.size[1], e.size[0], 3) for e in pil])
    else:
        arr = np.array(pil)
    return arr


def arr2pil(arr):
    "Numpy array => PIL"
    if arr.ndim == 3:
        return Image.fromarray(arr.astype('uint8'), 'RGB')
    elif arr.ndim == 4:
        return [Image.fromarray(e.astype('uint8'), 'RGB') for e in list(arr)]
    else:
        raise ValueError('arr must has ndim of 3 or 4, but got %s' % arr.ndim)



