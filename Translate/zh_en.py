from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline
from Obtain_Path import obtain_path
def translation(chinese):
    """
    input:
    chinese(str): 中文字符串


    output:
    result(dic): 由中文字符串翻译而来的英文字符串
    """

    #制作模型所在位置的绝对路径
    model_path = obtain_path()+'/Translate/translation_moudels'
    # 创建tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    # 创建模型
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    # 创建pipeline
    pipe = pipeline("translation", model=model, tokenizer=tokenizer)
    #运行模型，将中文字符串转为英文
    result = pipe(chinese)[0]['translation_text']
    return result
