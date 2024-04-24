from typing import List

from moudel_fuction.moudel_reference_fuction.facefusion.model.common_helper import create_int_range
from moudel_fuction.moudel_reference_fuction.facefusion.model.processors.frame.typings import FaceSwapperModel, FaceEnhancerModel

face_swapper_models : List[FaceSwapperModel] = [ 'blendswap_256', 'inswapper_128', 'inswapper_128_fp16', 'simswap_256', 'simswap_512_unofficial' ]
face_enhancer_models : List[FaceEnhancerModel] = [ 'codeformer', 'gfpgan_1.2', 'gfpgan_1.3', 'gfpgan_1.4', 'gpen_bfr_256', 'gpen_bfr_512', 'restoreformer_plus_plus' ]
face_enhancer_blend_range : List[int] = create_int_range(0, 100, 1)