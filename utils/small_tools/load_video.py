import requests
import imageio
from io import BytesIO
#加载本地或url路径上的事情
def load_video(file_path: str):
    if file_path.startswith(('http://', 'https://')):
        response = requests.get(file_path)
        response.raise_for_status()
        content = BytesIO(response.content)
        vid = imageio.get_reader(content)
    else:
        vid = imageio.get_reader(file_path)
    return vid
