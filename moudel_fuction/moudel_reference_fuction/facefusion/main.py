from model.test import process_video
from core.utils.tools import split_filename
from moudel_fuction.moudel_reference_fuction.facefusion.utils.face_detector import *
from Obtain_Path import resolve_relative_path
import traceback
from core.utils.tools import input_file
from moudel_fuction.moudel_reference_fuction.facefusion import cfg
from moudel_fuction.moudel_reference_fuction.facefusion.model.parameter import cli
import os

def facefusion_api(info,res_json):

	"""

	hu

	  input:
	  info (Json): 结构体
	      example:
	      {
	        "task_id" (Int): ,
	        "dist_dir" (String): ,
	        "source_file" (String): ,
	        "target_file" (String): ,
	        "frame_number" (Int): ,
	        "reference_face_position" (Int): ,
	        "reference_face_distance" (Int): ,
	        "face_selector_mode" (String): ,
	        "face_analyse_order" (String): ,
	        "face_analyse_age" (Int): "",
	        "face_analyse_gender" (Int): "",
	        "programe" (Int): 0,
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

	"参数初始化"
	cli()
	source = input_file(info['source_file'])
	target = input_file(info['target_file'])
	output_dir = info['dist_dir']
	cfg.source_paths = [source]
	cfg.target_path = target
	cfg.reference_face_distance = info['reference_face_distance']
	cfg.face_selector_mode = info['face_selector_mode']
	cfg.face_analyse_order = info['face_analyse_gender']
	cfg.face_analyse_age = info['face_analyse_age']
	cfg.face_analyse_gender = info['face_analyse_gender']
	cfg.reference_face_position = info['reference_face_position']

	if is_video(cfg.target_path):
		target_video_resolution = detect_video_resolution(cfg.target_path)
		cfg.output_video_resolution = pack_resolution(target_video_resolution)
		cfg.output_video_fps = detect_video_fps(cfg.target_path)

	if is_image(source):
		reference_frame = read_static_image(source)
		gallery_frames = extract_gallery_frames(reference_frame)
		if not gallery_frames:
			raise ValueError("Please provide a image/video with face.")
	elif is_video(source):
		reference_frame = get_video_frame(source, info['frame_number'])
		gallery_frames = extract_gallery_frames(reference_frame)
		if not gallery_frames:
			raise ValueError("Please provide a image/video with face.")
	else:
		raise ValueError('Invalid source file')

	if is_image(target):
		reference_frame = read_static_image(target)
		gallery_frames = extract_gallery_frames(reference_frame)
	elif is_video(target):
		reference_frame = get_video_frame(target, info['frame_number'])
		gallery_frames = extract_gallery_frames(reference_frame)
	else:
		raise ValueError('Invalid target file')


	if info['programe'] == 0:
		try:
			import time
			start = time.time()
			image = update_preview_image(frame_number=info['frame_number'])
			_, original_name, _ = split_filename(target)
			file_name = ('{}_{}').format(original_name.split(".")[0], str(info['frame_number']))
			name = file_name + '.jpg'
			output_path = resolve_relative_path(os.path.join(output_dir, name))
			image.save(output_path)
			preview_image_url = output_path

			reference_images = []
			if gallery_frames:
				for i, frame in enumerate(gallery_frames):
					frame_name = ('{}_{}.jpg').format(file_name, i)
					output_path = resolve_relative_path(os.path.join(output_dir, frame_name))
					frame.save(output_path)
					reference_images.append(output_path)
			end_time = time.time()
			print(end_time - start)

			return preview_image_url, reference_images

		except Exception as e:
			traceback.print_exc()
			return -1


	elif info['programe'] == 1:

		try:
			import time
			start = time.time()
			conditional_append_reference_faces()
			if is_image(cfg.target_path):
				image = update_preview_image(frame_number=0)
				_, original_name, _ = split_filename(target)
				name = original_name.split(".")[0] + '.jpg'
				output_path = resolve_relative_path(os.path.join(output_dir, name))
				image.save(output_path)
				video_url = output_path

			elif is_video(cfg.target_path):
				_, original_name, _ = split_filename(target)
				name = original_name.split(".")[0] + '.mp4'
				output_path = resolve_relative_path(os.path.join(output_dir, name))
				cfg.output_path = output_path
				process_video(start)
				video_url = output_path

			return video_url

		except Exception as e:

			traceback.print_exc()
			return -1


if __name__ == "__main__":

	"""
	Test Example
	"""

	info = {
		"task_id": 1,
		"dist_dir" : "E:/test",
		"source_file": "D:/face_test_example/source_image2.jpeg",
		"target_file": "D:/face_test_example/target-test.mp4",
		"frame_number": 130,
		"reference_face_position": 0,
		"reference_face_distance": 1,
		"face_selector_mode": "reference",
		"face_analyse_order": "left-right",
		"face_analyse_age": "child",
		"face_analyse_gender": "female",
		"programe": 0
}

	res_json_0 = {
		"task_id": int,
		'preview_image': "",
		'reference_images': "",
		"err_code": int,
		"err_msg": "",
	}

	res_json_1 = {
		"task_id": int,
		"video_url": "",
		"err_code": int,
		"err_msg": "",
	}

	res = facefusion_api(info, res_json_0)
	print(res)