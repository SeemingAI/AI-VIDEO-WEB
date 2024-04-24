from core.utils.vision import *

from ..model.face_analyser import *
from ..model.content_analyser import analyse_frame
from ..model.face_store import get_reference_faces

from ..model.processors.frame.test import load_frame_processor_module
from PIL import Image
import cv2
from moudel_fuction.moudel_reference_fuction.facefusion.model.test import conditional_append_reference_faces
from moudel_fuction.moudel_reference_fuction.facefusion.model import globals as cfg

def process_preview_frame(source_face, reference_faces, temp_frame):
	temp_frame = resize_frame_resolution(temp_frame, 640, 640)
	if analyse_frame(temp_frame):
		return cv2.GaussianBlur(temp_frame, (99, 99), 0)
		return cv2.GaussianBlur(temp_frame, (99, 99), 0)

	for frame_processor in cfg.frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		if frame_processor_module.pre_process('preview'):
			temp_frame = frame_processor_module.process_frame(
				source_face,
				reference_faces,
				temp_frame
			)
		return temp_frame

def update_preview_image(frame_number):
	for frame_processor in cfg.frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
	conditional_append_reference_faces()
	source_frames = read_static_images(cfg.source_paths)
	source_face = get_average_face(source_frames)  # get soure image information
	reference_faces = get_reference_faces() if 'reference' in cfg.face_selector_mode else None
	if is_image(cfg.target_path):
		target_frame = read_static_image(cfg.target_path)
		preview_frame = process_preview_frame(source_face, reference_faces, target_frame)
		preview_frame = normalize_frame_color(preview_frame)
		frame = Image.fromarray(preview_frame)
		return frame
	if is_video(cfg.target_path):
		temp_frame = get_video_frame(cfg.target_path, frame_number)
		preview_frame = process_preview_frame(source_face, reference_faces, temp_frame)
		preview_frame = normalize_frame_color(preview_frame)
		frame = Image.fromarray(preview_frame)
		return frame


def update_reference_position_gallery():
	gallery_frames = []
	if is_image(cfg.target_path):
		reference_frame = read_static_image(cfg.target_path)
		gallery_frames = extract_gallery_frames(reference_frame)
	if is_video(cfg.target_path):
		reference_frame = get_video_frame(cfg.target_path, cfg.reference_frame_number)
		gallery_frames = extract_gallery_frames(reference_frame)
	if gallery_frames:
		return gallery_frames

# crop frames
def extract_gallery_frames(reference_frame):
	face_lists = []
	faces = get_many_faces(reference_frame)

	if not faces:
		face_lists = []
	else:
		for i, face in enumerate(faces):
			start_x, start_y, end_x, end_y = map(int, face.bbox)
			padding_x = int((end_x - start_x) * 0.25)
			padding_y = int((end_y - start_y) * 0.25)
			start_x = max(0, start_x - padding_x)
			start_y = max(0, start_y - padding_y)
			end_x = max(0, end_x + padding_x)
			end_y = max(0, end_y + padding_y)
			crop_frame = reference_frame[start_y:end_y, start_x:end_x]
			crop_frame = normalize_frame_color(crop_frame)
			face_list = Image.fromarray(crop_frame)
			face_lists.append(face_list)
	return face_lists