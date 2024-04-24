import os
import signal
import sys
import time
import warnings
import shutil
import numpy
import onnxruntime
from time import sleep
from argparse import ArgumentParser, HelpFormatter

from .face_analyser import get_one_face, get_average_face
from .face_store import get_reference_faces, append_reference_face
from . import face_analyser, face_masker, content_analyser, logger, wording, parameter
from .content_analyser import analyse_image, analyse_video
from .processors.frame.test import get_frame_processors_modules, load_frame_processor_module
from .common_helper import create_metavar
from .execution_helper import encode_execution_providers, decode_execution_providers
from .normalizer import normalize_output_path, normalize_padding, normalize_fps
from .memory import limit_system_memory

from core.utils.file_process import get_temp_frame_paths, create_temp, move_temp, clear_temp
from core.utils.tools import list_directory, is_image, is_video
from core.utils.frame_to_video_ffmpeg import extract_frames, compress_image, merge_video, restore_audio
from core.utils.vision import get_video_frame, read_image, read_static_images, detect_video_resolution, detect_video_fps, create_video_resolutions
from moudel_fuction.moudel_reference_fuction.facefusion.model import globals as cfg
from core.utils.tools import split_filename

from queue import Queue

onnxruntime.set_default_logger_severity(3)
os.environ['OMP_NUM_THREADS'] = '1'
warnings.filterwarnings('ignore', category = UserWarning, module = 'gradio')
warnings.filterwarnings('ignore', category = UserWarning, module = 'torchvision')

def cli() -> None:
	signal.signal(signal.SIGINT, lambda signal_number, frame: destroy())
	program = ArgumentParser(formatter_class = lambda prog: HelpFormatter(prog, max_help_position = 120), add_help = False)
	# general
	program.add_argument('-s', '--source', help = wording.get('source_help'), action ='append', dest ='source_paths', default = parameter.get_str_list('general.source_paths'))
	program.add_argument('-t', '--target', help = wording.get('target_help'), dest ='target_path', default = args.get_str_value('general.target_path'))
	program.add_argument('-o', '--output', help = wording.get('output_help'), dest ='output_path', default = parameter.get_str_value('general.output_path'))
	# misc
	group_misc = program.add_argument_group('misc')
	group_misc.add_argument('--skip-download', help = wording.get('skip_download_help'), action ='store_true', default = parameter.get_bool_value('misc.skip_download'))
	group_misc.add_argument('--headless', help = wording.get('headless_help'), action ='store_true', default = parameter.get_bool_value('misc.headless'))
	group_misc.add_argument('--log-level', help = wording.get('log_level_help'), default = args.get_str_value('misc.log_level', 'info'), choices = logger.get_log_levels())
	# execution
	execution_providers = encode_execution_providers(onnxruntime.get_available_providers())
	group_execution = program.add_argument_group('execution')
	group_execution.add_argument('--execution-providers', help = wording.get('execution_providers_help').format(choices =', '.join(execution_providers)), default = args.get_str_list('execution.execution_providers', 'cpu'), choices = execution_providers, nargs ='+', metavar ='EXECUTION_PROVIDERS')
	group_execution.add_argument('--execution-thread-count', help = wording.get('execution_thread_count_help'), type = int, default = parameter.get_int_value('execution.execution_thread_count', '4'), choices = facefusion.choices.execution_thread_count_range, metavar = create_metavar(facefusion.choices.execution_thread_count_range))
	group_execution.add_argument('--execution-queue-count', help = wording.get('execution_queue_count_help'), type = int, default = args.get_int_value('execution.execution_queue_count', '1'), choices = facefusion.choices.execution_queue_count_range, metavar = create_metavar(facefusion.choices.execution_queue_count_range))
	# memory
	group_memory = program.add_argument_group('memory')
	group_memory.add_argument('--video-memory-strategy', help = wording.get('video_memory_strategy_help'), default = args.get_str_value('memory.video_memory_strategy', 'strict'), choices = facefusion.choices.video_memory_strategies)
	group_memory.add_argument('--system-memory-limit', help = wording.get('system_memory_limit_help'), type = int, default = config.get_int_value('memory.system_memory_limit', '0'), choices = facefusion.choices.system_memory_limit_range, metavar = create_metavar(facefusion.choices.system_memory_limit_range))
	# face analyser
	group_face_analyser = program.add_argument_group('face analyser')
	group_face_analyser.add_argument('--face-analyser-order', help = wording.get('face_analyser_order_help'), default = args.get_str_value('face_analyser.face_analyser_order', 'left-right'), choices = facefusion.choices.face_analyser_orders)
	group_face_analyser.add_argument('--face-analyser-age', help = wording.get('face_analyser_age_help'), default = args.get_str_value('face_analyser.face_analyser_age'), choices = facefusion.choices.face_analyser_ages)
	group_face_analyser.add_argument('--face-analyser-gender', help = wording.get('face_analyser_gender_help'), default = config.get_str_value('face_analyser.face_analyser_gender'), choices = facefusion.choices.face_analyser_genders)
	group_face_analyser.add_argument('--face-detector-model', help = wording.get('face_detector_model_help'), default = config.get_str_value('face_analyser.face_detector_model', 'retinaface'), choices = facefusion.choices.face_detector_models)
	group_face_analyser.add_argument('--face-detector-size', help = wording.get('face_detector_size_help'), default = parameter.get_str_value('face_analyser.face_detector_size', '640x640'), choices = facefusion.choices.face_detector_sizes)
	group_face_analyser.add_argument('--face-detector-score', help = wording.get('face_detector_score_help'), type = float, default = args.get_float_value('face_analyser.face_detector_score', '0.5'), choices = facefusion.choices.face_detector_score_range, metavar = create_metavar(facefusion.choices.face_detector_score_range))
	# face selector
	group_face_selector = program.add_argument_group('face selector')
	group_face_selector.add_argument('--face-selector-mode', help = wording.get('face_selector_mode_help'), default = args.get_str_value('face_selector.face_selector_mode', 'reference'), choices = facefusion.choices.face_selector_modes)
	group_face_selector.add_argument('--reference-face-position', help = wording.get('reference_face_position_help'), type = int, default = parameter.get_int_value('face_selector.reference_face_position', '0'))
	group_face_selector.add_argument('--reference-face-distance', help = wording.get('reference_face_distance_help'), type = float, default = parameter.get_float_value('face_selector.reference_face_distance', '0.6'), choices = facefusion.choices.reference_face_distance_range, metavar = create_metavar(facefusion.choices.reference_face_distance_range))
	group_face_selector.add_argument('--reference-frame-number', help = wording.get('reference_frame_number_help'), type = int, default = parameter.get_int_value('face_selector.reference_frame_number', '0'))
	# face mask
	group_face_mask = program.add_argument_group('face mask')
	group_face_mask.add_argument('--face-mask-types', help = wording.get('face_mask_types_help').format(choices =', '.join(facefusion.choices.face_mask_types)), default = args.get_str_list('face_mask.face_mask_types', 'box'), choices = facefusion.choices.face_mask_types, nargs ='+', metavar ='FACE_MASK_TYPES')
	group_face_mask.add_argument('--face-mask-blur', help = wording.get('face_mask_blur_help'), type = float, default = args.get_float_value('face_mask.face_mask_blur', '0.3'), choices = facefusion.choices.face_mask_blur_range, metavar = create_metavar(facefusion.choices.face_mask_blur_range))
	group_face_mask.add_argument('--face-mask-padding', help = wording.get('face_mask_padding_help'), type = int, default = parameter.get_int_list('face_mask.face_mask_padding', '0 0 0 0'), nargs ='+')
	group_face_mask.add_argument('--face-mask-regions', help = wording.get('face_mask_regions_help').format(choices =', '.join(facefusion.choices.face_mask_regions)), default = args.get_str_list('face_mask.face_mask_regions', ' '.join(facefusion.choices.face_mask_regions)), choices = facefusion.choices.face_mask_regions, nargs ='+', metavar ='FACE_MASK_REGIONS')
	# frame extraction
	group_frame_extraction = program.add_argument_group('frame extraction')
	group_frame_extraction.add_argument('--trim-frame-start', help = wording.get('trim_frame_start_help'), type = int, default = facefusion.utils.config.get_int_value('frame_extraction.trim_frame_start'))
	group_frame_extraction.add_argument('--trim-frame-end', help = wording.get('trim_frame_end_help'), type = int, default = facefusion.utils.config.get_int_value('frame_extraction.trim_frame_end'))
	group_frame_extraction.add_argument('--temp-frame-format', help = wording.get('temp_frame_format_help'), default = args.get_str_value('frame_extraction.temp_frame_format', 'jpg'), choices = facefusion.choices.temp_frame_formats)
	group_frame_extraction.add_argument('--temp-frame-quality', help = wording.get('temp_frame_quality_help'), type = int, default = parameter.get_int_value('frame_extraction.temp_frame_quality', '100'), choices = facefusion.choices.temp_frame_quality_range, metavar = create_metavar(facefusion.choices.temp_frame_quality_range))
	group_frame_extraction.add_argument('--keep-temp', help = wording.get('keep_temp_help'), action ='store_true', default = args.get_bool_value('frame_extraction.keep_temp'))
	# output creation
	group_output_creation = program.add_argument_group('output creation')
	group_output_creation.add_argument('--output-image-quality', help = wording.get('output_image_quality_help'), type = int, default = parameter.get_int_value('output_creation.output_image_quality', '80'), choices = facefusion.choices.output_image_quality_range, metavar = create_metavar(facefusion.choices.output_image_quality_range))
	group_output_creation.add_argument('--output-video-encoder', help = wording.get('output_video_encoder_help'), default = args.get_str_value('output_creation.output_video_encoder', 'libx264'), choices = facefusion.choices.output_video_encoders)
	group_output_creation.add_argument('--output-video-preset', help = wording.get('output_video_preset_help'), default = args.get_str_value('output_creation.output_video_preset', 'veryfast'), choices = facefusion.choices.output_video_presets)
	group_output_creation.add_argument('--output-video-quality', help = wording.get('output_video_quality_help'), type = int, default = parameter.get_int_value('output_creation.output_video_quality', '80'), choices = facefusion.choices.output_video_quality_range, metavar = create_metavar(facefusion.choices.output_video_quality_range))
	group_output_creation.add_argument('--output-video-resolution', help = wording.get('output_video_resolution_help'), default = parameter.get_str_value('output_creation.output_video_resolution'))
	group_output_creation.add_argument('--output-video-fps', help = wording.get('output_video_fps_help'), type = float)
	group_output_creation.add_argument('--skip-audio', help = wording.get('skip_audio_help'), action ='store_true', default = args.get_bool_value('output_creation.skip_audio'))
	# frame processors
	available_frame_processors = list_directory('model/processors/frame/modules')
	program = ArgumentParser(parents = [ program ], formatter_class = program.formatter_class, add_help = True)
	group_frame_processors = program.add_argument_group('frame processors')
	group_frame_processors.add_argument('--frame-processors', help = wording.get('frame_processors_help').format(choices =', '.join(available_frame_processors)), default = parameter.get_str_list('frame_processors.frame_processors', 'face_swapper'), nargs ='+')
	for frame_processor in available_frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		frame_processor_module.register_args(group_frame_processors)
	# uis
	available_ui_layouts = list_directory('model/uis/layouts')
	group_uis = program.add_argument_group('uis')
	group_uis.add_argument('--ui-layouts', help = wording.get('ui_layouts_help').format(choices =', '.join(available_ui_layouts)), default = args.get_str_list('uis.ui_layout', 'default'), nargs ='+')
	run(program)


def apply_args(program : ArgumentParser) -> None:
	args = program.parse_args()
	# general
	cfg.source_paths = args.source_paths
	cfg.target_path = args.target_path
	cfg.output_path = normalize_output_path(cfg.source_paths, cfg.target_path, args.output_path)
	# misc
	cfg.skip_download = args.skip_download
	cfg.headless = args.headless
	cfg.log_level = args.log_level
	# execution
	cfg.execution_providers = decode_execution_providers(args.execution_providers)
	cfg.execution_thread_count = args.execution_thread_count
	cfg.execution_queue_count = args.execution_queue_count
	# memory
	cfg.video_memory_strategy = args.video_memory_strategy
	cfg.system_memory_limit = args.system_memory_limit
	# face analyser
	cfg.face_analyser_order = args.face_analyser_order
	cfg.face_analyser_age = args.face_analyser_age
	cfg.face_analyser_gender = args.face_analyser_gender
	cfg.face_detector_model = args.face_detector_model
	cfg.face_detector_size = args.face_detector_size
	cfg.face_detector_score = args.face_detector_score
	# face selector
	cfg.face_selector_mode = args.face_selector_mode
	cfg.reference_face_position = args.reference_face_position
	cfg.reference_face_distance = args.reference_face_distance
	cfg.reference_frame_number = args.reference_frame_number
	# face mask
	cfg.face_mask_types = args.face_mask_types
	cfg.face_mask_blur = args.face_mask_blur
	cfg.face_mask_padding = normalize_padding(args.face_mask_padding)
	cfg.face_mask_regions = args.face_mask_regions
	# frame extraction
	cfg.trim_frame_start = args.trim_frame_start
	cfg.trim_frame_end = args.trim_frame_end
	cfg.temp_frame_format = args.temp_frame_format
	cfg.temp_frame_quality = args.temp_frame_quality
	cfg.keep_temp = args.keep_temp
	# output creation
	cfg.output_image_quality = args.output_image_quality
	cfg.output_video_encoder = args.output_video_encoder
	cfg.output_video_preset = args.output_video_preset
	cfg.output_video_quality = args.output_video_quality
	if is_video(args.target_path):
		target_video_resolutions = create_video_resolutions(args.target_path)
		if args.output_video_resolution in target_video_resolutions:
			cfg.output_video_resolution = args.output_video_resolution
		else:
			target_video_resolution = detect_video_resolution(args.target_path)
			cfg.output_video_resolution = target_video_resolution
	if args.output_video_fps or is_video(args.target_path):
		cfg.output_video_fps = normalize_fps(args.output_video_fps) or detect_video_fps(args.target_path)
	cfg.skip_audio = args.skip_audio
	# frame processors
	available_frame_processors = list_directory('model/processors/frame/modules')
	cfg.frame_processors = args.frame_processors
	for frame_processor in available_frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		frame_processor_module.apply_args(program)
	# uis
	cfg.ui_layouts = args.ui_layouts


def run(program : ArgumentParser) -> None:
	apply_args(program)
	logger.init(cfg.log_level)
	if cfg.system_memory_limit > 0:
		limit_system_memory(cfg.system_memory_limit)

	#check model path and selecet model
	if not pre_check() or not content_analyser.pre_check() or not face_analyser.pre_check() or not face_masker.pre_check():
		return
	for frame_processor_module in get_frame_processors_modules(cfg.frame_processors):
		if not frame_processor_module.pre_check():
			return
	if cfg.headless:
		conditional_process()
	else:
		import facefusion.uis.core as ui

		for ui_layout in ui.get_ui_layouts_modules(cfg.ui_layouts):
			if not ui_layout.pre_check():
				return
		ui.launch()


def destroy() -> None:
	if cfg.target_path:
		clear_temp(cfg.target_path)
	sys.exit(0)


def pre_check() -> bool:
	if sys.version_info < (3, 9):
		logger.error(wording.get('python_not_supported').format(version ='3.9'), __name__.upper())
		return False
	if not shutil.which('ffmpeg'):
		logger.error(wording.get('ffmpeg_not_installed'), __name__.upper())
		return False
	return True


def conditional_process() -> None:
	start_time = time.time()
	for frame_processor_module in get_frame_processors_modules(cfg.frame_processors):
		while not frame_processor_module.post_check():
			logger.disable()
			sleep(0.5)
		logger.enable()
		if not frame_processor_module.pre_process('output'):
			return
	conditional_append_reference_faces()
	if is_image(cfg.target_path):
		process_image(start_time)
	if is_video(cfg.target_path):
		process_video(start_time)


def conditional_append_reference_faces() -> None:
	if 'reference' in cfg.face_selector_mode and not get_reference_faces():
		source_frames = read_static_images(cfg.source_paths)
		source_face = get_average_face(source_frames)
		if is_video(cfg.target_path):
			reference_frame = get_video_frame(cfg.target_path, cfg.reference_frame_number)
		else:
			reference_frame = read_image(cfg.target_path)
		reference_face = get_one_face(reference_frame, cfg.reference_face_position)
		append_reference_face('origin', reference_face)
		if source_face and reference_face:
			for frame_processor_module in get_frame_processors_modules(cfg.frame_processors):
				abstract_reference_frame = frame_processor_module.get_reference_frame(source_face, reference_face, reference_frame)
				if numpy.any(abstract_reference_frame):
					reference_frame = abstract_reference_frame
					reference_face = get_one_face(reference_frame, cfg.reference_face_position)
					append_reference_face(frame_processor_module.__name__, reference_face)


def process_image(start_time : float) -> None:
	if analyse_image(cfg.target_path):
		return
	shutil.copy2(cfg.target_path, cfg.output_path)
	# process frame
	for frame_processor_module in get_frame_processors_modules(cfg.frame_processors):
		logger.info(wording.get('processing'), frame_processor_module.NAME)
		frame_processor_module.process_image(cfg.source_paths, cfg.output_path, cfg.output_path)
		frame_processor_module.post_process()
	# compress image
	logger.info(wording.get('compressing_image'), __name__.upper())
	if not compress_image(cfg.output_path):
		logger.error(wording.get('compressing_image_failed'), __name__.upper())
	# validate image
	if is_image(cfg.output_path):
		seconds = '{:.2f}'.format((time.time() - start_time) % 60)
		logger.info(wording.get('processing_image_succeed').format(seconds = seconds), __name__.upper())
	else:
		logger.error(wording.get('processing_image_failed'), __name__.upper())


def process_video(start_time : float) -> None:
	if analyse_video(cfg.target_path,start_frame=0, end_frame=0):
		return
	# create temp
	logger.info(wording.get('creating_temp'), __name__.upper())
	create_temp(cfg.target_path)
	# extract frames
	logger.info(wording.get('extracting_frames_fps').format(video_fps = cfg.output_video_fps), __name__.upper())
	extract_frames(cfg.target_path, cfg.output_video_resolution, cfg.output_video_fps)
	# process frame
	temp_frame_paths = get_temp_frame_paths(cfg.target_path)
	if temp_frame_paths:
		for frame_processor_module in get_frame_processors_modules(cfg.frame_processors):
			logger.info(wording.get('processing'), frame_processor_module.NAME)
			frame_processor_module.process_video(cfg.source_paths, temp_frame_paths)
			frame_processor_module.post_process()
	else:
		logger.error(wording.get('temp_frames_not_found'), __name__.upper())
		return
	# merge video
	logger.info(wording.get('merging_video_fps').format(video_fps = cfg.output_video_fps), __name__.upper())
	_,name,_ = split_filename(cfg.target_path)
	temp_output_video_path, flag = merge_video(cfg.target_path, cfg.output_video_resolution, cfg.output_video_fps, name)
	if not flag:
		logger.error(wording.get('merging_video_failed'), __name__.upper())
		return
	# handle audio
	if cfg.skip_audio:
		logger.info(wording.get('skipping_audio'), __name__.upper())
		move_temp(temp_output_video_path, cfg.output_path)
	else:
		logger.info(wording.get('restoring_audio'), __name__.upper())
		if not restore_audio(cfg.target_path, cfg.output_path, name):
			logger.warn(wording.get('restoring_audio_skipped'), __name__.upper())
			move_temp(temp_output_video_path, cfg.output_path)
	# clear temp
	logger.info(wording.get('clearing_temp'), __name__.upper())
	clear_temp(cfg.target_path)
	# validate video
	if is_video(cfg.output_path):
		seconds = '{:.2f}'.format((time.time() - start_time))
		logger.info(wording.get('processing_video_succeed').format(seconds = seconds), __name__.upper())
	else:
		logger.error(wording.get('processing_video_failed'), __name__.upper())

