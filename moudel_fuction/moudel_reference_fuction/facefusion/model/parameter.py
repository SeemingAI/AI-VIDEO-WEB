from moudel_fuction.moudel_reference_fuction.facefusion.model import config, wording, logger, choices
from .common_helper import create_metavar
from .execution_helper import encode_execution_providers, decode_execution_providers
from .normalizer import normalize_output_path, normalize_padding, normalize_fps
from core.utils.vision import pack_resolution, detect_video_resolution, \
	detect_video_fps, create_video_resolutions
from .processors.frame.test import load_frame_processor_module
from core.utils.tools import list_directory, is_video
from Obtain_Path import resolve_relative_path
from moudel_fuction.moudel_reference_fuction.facefusion.model.test import *

import onnxruntime
from argparse import ArgumentParser, HelpFormatter
from moudel_fuction.moudel_reference_fuction.facefusion import model
from moudel_fuction.moudel_reference_fuction.facefusion.model import globals as cfg

def cli():
	signal.signal(signal.SIGINT, lambda signal_number, frame: destroy())
	program = ArgumentParser(formatter_class=lambda prog: HelpFormatter(prog, max_help_position=120), add_help=False)
	# general
	program.add_argument('-s', '--source', help=wording.get('source_help'), action='append', dest='source_paths',
						 default=config.get_str_list('general.source_paths'))
	program.add_argument('-t', '--target', help=wording.get('target_help'), dest='target_path',
						 default=config.get_str_value('general.target_path'))
	program.add_argument('-o', '--output', help=wording.get('output_help'), dest='output_path',
                         default=config.get_str_value('general.output_path'))
	# misc
	group_misc = program.add_argument_group('misc')
	group_misc.add_argument('--skip-download', help=wording.get('skip_download_help'), action='store_true',
							default=config.get_bool_value('misc.skip_download'))

	# execution
	execution_providers = encode_execution_providers(onnxruntime.get_available_providers())
	group_execution = program.add_argument_group('execution')
	group_execution.add_argument('--execution-providers', help=wording.get('execution_providers_help').format(
		choices=', '.join(execution_providers)), default=config.get_str_list('execution.execution_providers', 'cpu'),
								 choices=execution_providers, nargs='+', metavar='EXECUTION_PROVIDERS')
	group_execution.add_argument('--execution-thread-count', help=wording.get('execution_thread_count_help'), type=int,
								 default=config.get_int_value('execution.execution_thread_count', '4'),
								 choices=choices.execution_thread_count_range,
								 metavar=create_metavar(choices.execution_thread_count_range))
	group_execution.add_argument('--execution-queue-count', help=wording.get('execution_queue_count_help'), type=int,
								 default=config.get_int_value('execution.execution_queue_count', '1'),
								 choices=choices.execution_queue_count_range,
								 metavar=create_metavar(choices.execution_queue_count_range))
	# memory
	group_memory = program.add_argument_group('memory')
	group_memory.add_argument('--video-memory-strategy', help=wording.get('video_memory_strategy_help'),
							  default=config.get_str_value('memory.video_memory_strategy', 'strict'),
							  choices=choices.video_memory_strategies)
	group_memory.add_argument('--system-memory-limit', help=wording.get('system_memory_limit_help'), type=int,
                              default=config.get_int_value('memory.system_memory_limit', '0'),
                              choices=choices.system_memory_limit_range,
                              metavar=create_metavar(choices.system_memory_limit_range))
	# face analyser
	group_face_analyser = program.add_argument_group('face analyser')
	group_face_analyser.add_argument('--face-analyser-order', help=wording.get('face_analyser_order_help'),
									 default=config.get_str_value('face_analyser.face_analyser_order', 'left-right'),
									 choices=choices.face_analyser_orders)
	group_face_analyser.add_argument('--face-analyser-age', help=wording.get('face_analyser_age_help'),
									 default=config.get_str_value('face_analyser.face_analyser_age'),
									 choices=choices.face_analyser_ages)
	group_face_analyser.add_argument('--face-analyser-gender', help=wording.get('face_analyser_gender_help'),
									 default=config.get_str_value('face_analyser.face_analyser_gender'),
									 choices=choices.face_analyser_genders)
	group_face_analyser.add_argument('--face-detector-model', help=wording.get('face_detector_model_help'),
									 default=config.get_str_value('face_analyser.face_detector_model', 'retinaface'),
									 choices=choices.face_detector_models)
	group_face_analyser.add_argument('--face-detector-size', help=wording.get('face_detector_size_help'),
									 default=config.get_str_value('face_analyser.face_detector_size', '640x640'),
									 choices=choices.face_detector_sizes)
	group_face_analyser.add_argument('--face-detector-score', help=wording.get('face_detector_score_help'), type=float,
									 default=config.get_float_value('face_analyser.face_detector_score', '0.5'),
									 choices=choices.face_detector_score_range,
									 metavar=create_metavar(choices.face_detector_score_range))
	# face selector
	group_face_selector = program.add_argument_group('face selector')
	group_face_selector.add_argument('--face-selector-mode', help=wording.get('face_selector_mode_help'),
                                     default=config.get_str_value('face_selector.face_selector_mode', 'reference'),
                                     choices=choices.face_selector_modes)
	group_face_selector.add_argument('--reference-face-position', help=wording.get('reference_face_position_help'),
									 type=int,
									 default=config.get_int_value('face_selector.reference_face_position', '0'))
	group_face_selector.add_argument('--reference-face-distance', help=wording.get('reference_face_distance_help'),
									 type=float,
									 default=config.get_float_value('face_selector.reference_face_distance', '0.6'),
									 choices=choices.reference_face_distance_range,
									 metavar=create_metavar(choices.reference_face_distance_range))
	group_face_selector.add_argument('--reference-frame-number', help=wording.get('reference_frame_number_help'),
                                     type=int,
                                     default=config.get_int_value('face_selector.reference_frame_number', '0'))
	# face mask
	group_face_mask = program.add_argument_group('face mask')
	group_face_mask.add_argument('--face-mask-types', help=wording.get('face_mask_types_help').format(
		choices=', '.join(choices.face_mask_types)),
                                 default=config.get_str_list('face_mask.face_mask_types', 'box'),
                                 choices=choices.face_mask_types, nargs='+', metavar='FACE_MASK_TYPES')
	group_face_mask.add_argument('--face-mask-blur', help=wording.get('face_mask_blur_help'), type=float,
                                 default=config.get_float_value('face_mask.face_mask_blur', '0.3'),
                                 choices=choices.face_mask_blur_range,
                                 metavar=create_metavar(choices.face_mask_blur_range))
	group_face_mask.add_argument('--face-mask-padding', help=wording.get('face_mask_padding_help'), type=int,
								 default=config.get_int_list('face_mask.face_mask_padding', '0 0 0 0'), nargs='+')
	group_face_mask.add_argument('--face-mask-regions', help=wording.get('face_mask_regions_help').format(
		choices=', '.join(choices.face_mask_regions)),
								 default=config.get_str_list('face_mask.face_mask_regions',
															 ' '.join(choices.face_mask_regions)),
								 choices=choices.face_mask_regions, nargs='+', metavar='FACE_MASK_REGIONS')

	# output creation
	group_output_creation = program.add_argument_group('output creation')
	group_output_creation.add_argument('--output-image-quality', help=wording.get('output_image_quality_help'),
									   type=int,
									   default=config.get_int_value('output_creation.output_image_quality', '80'),
									   choices=choices.output_image_quality_range,
									   metavar=create_metavar(choices.output_image_quality_range))
	group_output_creation.add_argument('--output-video-encoder', help=wording.get('output_video_encoder_help'),
                                       default=config.get_str_value('output_creation.output_video_encoder', 'libx264'),
                                       choices=choices.output_video_encoders)
	group_output_creation.add_argument('--output-video-preset', help=wording.get('output_video_preset_help'),
                                       default=config.get_str_value('output_creation.output_video_preset', 'veryfast'),
                                       choices=choices.output_video_presets)
	group_output_creation.add_argument('--output-video-quality', help=wording.get('output_video_quality_help'),
                                       type=int,
                                       default=config.get_int_value('output_creation.output_video_quality', '80'),
                                       choices=choices.output_video_quality_range,
                                       metavar=create_metavar(choices.output_video_quality_range))
	group_output_creation.add_argument('--output-video-resolution', help=wording.get('output_video_resolution_help'),
									   default=config.get_str_value('output_creation.output_video_resolution'))
	group_output_creation.add_argument('--output-video-fps', help=wording.get('output_video_fps_help'), type=float)
	group_output_creation.add_argument('--skip-audio', help=wording.get('skip_audio_help'), action='store_true',
									   default=config.get_bool_value('output_creation.skip_audio'))
	# frame processors
	available_frame_processors = list_directory(resolve_relative_path('moudel_fuction/moudel_reference_fuction/facefusion/model/processors/frame/modules'))
	program = ArgumentParser(parents=[program], formatter_class=program.formatter_class, add_help=True)
	group_frame_processors = program.add_argument_group('frame processors')
	group_frame_processors.add_argument('--frame-processors', help=wording.get('frame_processors_help').format(
		choices=', '.join(available_frame_processors)), default=config.get_str_list('frame_processors.frame_processors',
																					'face_swapper'), nargs='+')
	for frame_processor in available_frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		frame_processor_module.register_args(group_frame_processors)
	apply_args(program)


def apply_args(program: ArgumentParser):
	args = program.parse_args()
	# general
	cfg.source_paths = args.source_paths
	cfg.target_path = args.target_path
	cfg.output_path = normalize_output_path(cfg.source_paths, cfg.target_path, args.output_path)
	# misc
	cfg.skip_download = args.skip_download

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
			cfg.output_video_resolution = pack_resolution(target_video_resolution)
	if args.output_video_fps or is_video(args.target_path):
		cfg.output_video_fps = normalize_fps(args.output_video_fps) or detect_video_fps(args.target_path)
	cfg.skip_audio = args.skip_audio
	# frame processors
	available_frame_processors = list_directory(resolve_relative_path('moudel_fuction/moudel_reference_fuction/facefusion/model/processors/frame/modules'))
	cfg.frame_processors = args.frame_processors
	for frame_processor in available_frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		frame_processor_module.apply_args(program)