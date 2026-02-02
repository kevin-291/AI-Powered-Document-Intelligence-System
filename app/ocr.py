import easyocr
import numpy as np
import cv2
import logging

reader = easyocr.Reader(['en']) 
logger = logging.getLogger(__name__)

def _is_blurry(img, size: int = 60, blur_thresh: float = 32.0) -> bool:
    (h, w) = img.shape
    (cX, cY) = (int(w / 2.0), int(h / 2.0))
    fft = np.fft.fft2(img)
    fftShift = np.fft.fftshift(fft)
    fftShift[cY - size:cY + size, cX - size:cX + size] = 0
    fftShift = np.fft.ifftshift(fftShift)
    recon = np.fft.ifft2(fftShift)
    magnitude = 20 * np.log(np.abs(recon))
    return np.mean(magnitude) <= blur_thresh

def _sharpen_image(img):
    blurred = cv2.GaussianBlur(img, (7, 7), sigmaX=3)
    return cv2.addWeighted(img, 3.5, blurred, -2.5, 0)

def extract_text(image_bytes: bytes) -> str:
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Invalid image data")
        
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if _is_blurry(gray_img):
            gray_img = _sharpen_image(gray_img)

        result = reader.readtext(gray_img, detail=0)
        full_text = " ".join(result)
        return full_text
    
    except Exception as e:
        logger.error(f"OCR Extraction failed: {e}")
        raise e