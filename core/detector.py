from typing import Dict
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

LM = {
    # common / front
    "top": 10,
    "glabella": 9,
    "chin": 152,
    "left_face": 234,
    "right_face": 454,
    "left_zygion": 234,
    "right_zygion": 454,
    "left_jaw": 136,
    "right_jaw": 365,
    "left_temple": 54,
    "right_temple": 284,

    "left_eye_outer": 33,
    "left_eye_inner": 133,
    "right_eye_inner": 362,
    "right_eye_outer": 263,

    "left_upper_lid": 159,
    "right_upper_lid": 386,
    "left_lower_lid": 145,
    "right_lower_lid": 374,

    "left_brow_inner": 55,
    "left_brow_mid": 105,
    "left_brow_outer": 70,
    "right_brow_inner": 285,
    "right_brow_mid": 334,
    "right_brow_outer": 300,

    "nose_tip": 1,
    "subnasale": 2,
    "nose_left": 129,
    "nose_right": 358,
    "nose_bridge_upper": 6,
    "columella": 94,

    "upper_lip_outer": 0,
    "upper_lip_inner": 13,
    "lower_lip_inner": 14,
    "lower_lip_outer": 17,
    "mouth_left": 61,
    "mouth_right": 291,
    "philtrum_top": 0,
    "philtrum_base": 2,

    "left_cheek": 205,
    "right_cheek": 425,

    # side
    "upper_lip_front": 0,
    "lower_lip_front": 17,
    "pogonion": 152,
    "gonion_proxy": 365,
    "cervical_point": 378,
    "forehead_profile": 10,
    "browridge_profile": 70,
}


class LandmarkDetector:
    def __init__(self, model_path: str):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            min_face_detection_confidence=0.15,
            min_face_presence_confidence=0.15,
            min_tracking_confidence=0.15,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def _run(self, img_bgr):
        h, w = img_bgr.shape[:2]
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_img)
        if result.face_landmarks:
            return img_bgr, result.face_landmarks[0], w, h
        return None

    def _rotate_image(self, img, angle_deg):
        h, w = img.shape[:2]
        center = (w / 2, h / 2)
        mat = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
        rotated = cv2.warpAffine(
            img,
            mat,
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255),
        )
        return rotated, mat

    def _invert_affine_on_landmarks(self, landmarks, mat, w, h):
        inv = cv2.invertAffineTransform(mat)
        for lm in landmarks:
            px = lm.x * w
            py = lm.y * h
            x2 = inv[0, 0] * px + inv[0, 1] * py + inv[0, 2]
            y2 = inv[1, 0] * px + inv[1, 1] * py + inv[1, 2]
            lm.x = x2 / w
            lm.y = y2 / h

    def detect(self, file_bytes: bytes):
        npimg = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image file")

        out = self._run(img)
        if out:
            return out

        raise ValueError(
            "No face detected. Use a clear image with the full face visible and some space around it."
        )

    def detect_with_fallbacks(self, file_bytes: bytes):
        npimg = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image file")

        h, w = img.shape[:2]

        def remap_from_padded(landmarks, pw, ph, pad, orig_w, orig_h):
            for lm in landmarks:
                px = lm.x * pw - pad
                py = lm.y * ph - pad
                lm.x = px / orig_w
                lm.y = py / orig_h

        # 1) original
        out = self._run(img)
        if out:
            return out

        # 2) horizontal flip
        flipped = cv2.flip(img, 1)
        out = self._run(flipped)
        if out:
            _, landmarks, fw, fh = out
            for lm in landmarks:
                lm.x = 1.0 - lm.x
            return img, landmarks, w, h

        # 3) padded
        pad = int(max(h, w) * 0.20)
        padded = cv2.copyMakeBorder(
            img, pad, pad, pad, pad,
            cv2.BORDER_CONSTANT,
            value=(255, 255, 255)
        )
        out = self._run(padded)
        if out:
            _, landmarks, pw, ph = out
            remap_from_padded(landmarks, pw, ph, pad, w, h)
            return img, landmarks, w, h

        # 4) rotations
        for ang in (-25, -18, -12, -8, -5, 5, 8, 12, 18, 25):
            rotated, mat = self._rotate_image(img, ang)
            out = self._run(rotated)
            if out:
                _, landmarks, rw, rh = out
                self._invert_affine_on_landmarks(landmarks, mat, rw, rh)
                return img, landmarks, w, h

        # 5) padded + rotations
        pad = int(max(h, w) * 0.24)
        padded = cv2.copyMakeBorder(
            img, pad, pad, pad, pad,
            cv2.BORDER_CONSTANT,
            value=(255, 255, 255)
        )
        ph, pw = padded.shape[:2]
        for ang in (-25, -18, -12, -8, -5, 5, 8, 12, 18, 25):
            rotated, mat = self._rotate_image(padded, ang)
            out = self._run(rotated)
            if out:
                _, landmarks, rw, rh = out
                self._invert_affine_on_landmarks(landmarks, mat, rw, rh)
                remap_from_padded(landmarks, pw, ph, pad, w, h)
                return img, landmarks, w, h

        # 6) resized retries
        for target_w in (960, 768, 640, 512):
            scale = target_w / float(w)
            target_h = max(1, int(round(h * scale)))
            resized = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
            out = self._run(resized)
            if out:
                _, landmarks, rw, rh = out
                for lm in landmarks:
                    px = (lm.x * rw) / scale
                    py = (lm.y * rh) / scale
                    lm.x = px / w
                    lm.y = py / h
                return img, landmarks, w, h

        # 7) CLAHE enhancement
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l2 = clahe.apply(l)
        enhanced = cv2.cvtColor(cv2.merge([l2, a, b]), cv2.COLOR_LAB2BGR)

        out = self._run(enhanced)
        if out:
            _, landmarks, ew, eh = out
            return enhanced, landmarks, ew, eh

        # 8) CLAHE + padding + resize
        pad = int(max(h, w) * 0.22)
        enhanced_padded = cv2.copyMakeBorder(
            enhanced, pad, pad, pad, pad,
            cv2.BORDER_CONSTANT,
            value=(255, 255, 255)
        )
        eph, epw = enhanced_padded.shape[:2]

        for target_w in (1024, 896, 768, 640):
            scale = target_w / float(epw)
            target_h = max(1, int(round(eph * scale)))
            resized = cv2.resize(enhanced_padded, (target_w, target_h), interpolation=cv2.INTER_AREA)
            out = self._run(resized)
            if out:
                _, landmarks, rw, rh = out
                for lm in landmarks:
                    px = (lm.x * rw) / scale - pad
                    py = (lm.y * rh) / scale - pad
                    lm.x = px / w
                    lm.y = py / h
                return img, landmarks, w, h

        raise ValueError(
            "No face detected. For side analysis, use a true side profile with visible forehead, nose, lips, chin, neck, and some empty background around the head."
        )


def crop_face(img, face_landmarks):
    h, w = img.shape[:2]
    xs = [int(lm.x * w) for lm in face_landmarks]
    ys = [int(lm.y * h) for lm in face_landmarks]

    pad = int(max(max(xs) - min(xs), max(ys) - min(ys)) * 0.22)
    x1 = max(0, min(xs) - pad)
    y1 = max(0, min(ys) - pad)
    x2 = min(w, max(xs) + pad)
    y2 = min(h, max(ys) + pad)

    return img[y1:y2, x1:x2].copy(), (x1, y1)


def get_point(face_landmarks, idx: int, w: int, h: int, offset=(0, 0)) -> Dict[str, float]:
    lm = face_landmarks[idx]
    return {
        "x": float(lm.x * w - offset[0]),
        "y": float(lm.y * h - offset[1]),
    }


def collect_named_points(face_landmarks, w: int, h: int, offset=(0, 0)):
    return {
        name: get_point(face_landmarks, idx, w, h, offset)
        for name, idx in LM.items()
    }