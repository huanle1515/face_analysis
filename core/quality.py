import cv2
import numpy as np


def assess_image_quality(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))

    return {
        "blur_score": round(blur, 2),
        "brightness": round(brightness, 2),
        "is_blurry": bool(blur < 40.0),
        "is_dark": bool(brightness < 50.0),
        "is_overbright": bool(brightness > 220.0),
    }