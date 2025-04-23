import pytesseract
from PIL import Image
import os
import cv2
from ocr_preprocess import preprocess_image

# 支持的语言映射
SUPPORTED_LANGUAGES = {
    "jpn": "日文",
    "eng": "英文",
    "chi_sim": "简体中文",
    "chi_tra": "繁體中文",
}

def extract_text(image_path: str, lang: str = "jpn", use_preprocess=True) -> str:
    """
    对发票图片进行 OCR 识别，支持语言切换和图像预处理
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ 文件不存在：{image_path}")
    
    if lang not in SUPPORTED_LANGUAGES:
        print(f"⚠️ 不支持的语言：{lang}，默认使用 jpn")
        lang = "jpn"

    try:
        if use_preprocess:
            processed = preprocess_image(image_path)
            pil_img = Image.fromarray(processed)
        else:
            pil_img = Image.open(image_path)

        text = pytesseract.image_to_string(pil_img, lang=lang)
        return text.strip()
    
    except Exception as e:
        print(f"❌ OCR 失败：{e}")
        return ""

# ✅ 测试入口
if __name__ == "__main__":
    test_path = "../sample_data/test_invoice.jpg"  # 你自己的发票图像路径
    lang = "jpn"  # 可改为 eng / chi_sim / chi_tra
    print(f"🔍 正在识别 [{SUPPORTED_LANGUAGES.get(lang, lang)}]：{test_path}\n")

    result = extract_text(test_path, lang=lang, use_preprocess=True)
    print("✅ 识别结果：\n", result)
