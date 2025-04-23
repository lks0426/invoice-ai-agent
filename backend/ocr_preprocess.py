import cv2
import numpy as np

def preprocess_image(image_path: str, save_path: str = None) -> np.ndarray:
    """
    使用 OpenCV 对图片进行预处理，提高 OCR 识别率
    步骤：灰度化 -> 高斯模糊 -> 自适应阈值二值化
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"❌ 图像文件无法读取：{image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    if save_path:
        cv2.imwrite(save_path, thresh)

    return thresh
