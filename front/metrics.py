from core.geometry import horizontal_dist, vertical_dist, midpoint
from front.overlay_builders import (
    eye_spacing_overlay,
    width_height_overlay,
    nose_width_overlay,
    symmetry_overlay,
    generic_horizontal_ratio_overlay,
    brow_alignment_overlay,
    lip_ratio_overlay,
)


def compute_front_metrics(points, d):
    bizygomatic_w = horizontal_dist(d["left_face_stable"], d["right_face_stable"])
    face_h = vertical_dist(d["top_stable"], d["chin_stable"])
    jaw_w = horizontal_dist(d["left_jaw_stable"], d["right_jaw_stable"])

    # FaceIQ-like eye spacing uses pupil/eye-center distance relative to bizygomatic width
    interpupillary_dist = horizontal_dist(d["left_eye_center"], d["right_eye_center"])

    # Use improved alar points if present, otherwise fallback
    nose_left = d.get("left_alar", points["nose_left"])
    nose_right = d.get("right_alar", points["nose_right"])
    nose_w = horizontal_dist(nose_left, nose_right)

    upper_lip_h = vertical_dist(points["upper_lip_outer"], points["upper_lip_inner"])
    lower_lip_h = vertical_dist(points["lower_lip_inner"], points["lower_lip_outer"])

    center_x = d["face_center_x"]
    eye_mid = midpoint(d["left_eye_center"], d["right_eye_center"])

    # Symmetry
    asym = (
        abs(points["nose_tip"]["x"] - center_x) +
        abs(d["mouth_center"]["x"] - center_x) +
        abs(eye_mid["x"] - center_x)
    ) / 3.0
    symmetry = max(0.0, 100.0 * (1.0 - asym / max(bizygomatic_w * 0.10, 1.0)))

    # Nose deviation from centerline
    nose_dev = abs(points["nose_tip"]["x"] - center_x) / max(bizygomatic_w * 1.15, 1e-6) * 100.0

    # Brow alignment
    brow_tilt_ratio = abs(points["left_brow_mid"]["y"] - points["right_brow_mid"]["y"]) / max(face_h, 1e-6)
    brow_alignment = max(0.0, 100.0 * (1.0 - brow_tilt_ratio / 0.045))

    # Eye cant
    eye_tilt = abs(d["right_eye_center"]["y"] - d["left_eye_center"]["y"]) / max(bizygomatic_w, 1e-6) * 100.0

    # Main ratios
    facial_w_to_h = face_h / max(bizygomatic_w, 1e-6)

    # Restored calibrated version for better practical accuracy
    eye_spacing_percent = (interpupillary_dist / max(bizygomatic_w * 1.08, 1e-6)) * 100.0
    jaw_width = (jaw_w * 0.95) / max(bizygomatic_w, 1e-6)
    nose_width_ratio = (nose_w * 0.88) / max(bizygomatic_w, 1e-6)
    lip_ratio = lower_lip_h / max(upper_lip_h, 1e-6)

    metrics = {
        "facial_width_to_height_ratio": {
            "value": round(facial_w_to_h, 2),
            "value_display": f"{facial_w_to_h:.2f}x",
            "overlay": width_height_overlay(d, f"{facial_w_to_h:.2f}x"),
        },
        "facial_symmetry": {
            "value": round(symmetry, 2),
            "value_display": f"{symmetry:.0f}%",
            "overlay": symmetry_overlay(points, d, f"{symmetry:.0f}%"),
        },
        "eye_spacing_ratio": {
            "value": round(eye_spacing_percent, 1),
            "value_display": f"{eye_spacing_percent:.1f}%",
            "overlay": eye_spacing_overlay(d, f"{eye_spacing_percent:.1f}%"),
        },
        "jaw_width": {
            "value": round(jaw_width, 2),
            "value_display": f"{jaw_width:.2f}x",
            "overlay": generic_horizontal_ratio_overlay(
                d["left_jaw_stable"],
                d["right_jaw_stable"],
                d["left_face_stable"],
                d["right_face_stable"],
                f"{jaw_width:.2f}x"
            ),
        },
        "lip_ratio": {
            "value": round(lip_ratio, 2),
            "value_display": f"1:{lip_ratio:.2f}",
            "overlay": lip_ratio_overlay(points, f"1:{lip_ratio:.2f}"),
        },
        "nose_width_ratio": {
            "value": round(nose_width_ratio, 2),
            "value_display": f"{nose_width_ratio:.2f}x",
            "overlay": nose_width_overlay(
                {
                    **points,
                    "nose_left": nose_left,
                    "nose_right": nose_right,
                },
                d,
                f"{nose_width_ratio:.2f}x"
            ),
        },
        "brow_alignment": {
            "value": round(brow_alignment, 2),
            "value_display": f"{brow_alignment:.0f}%",
            "overlay": brow_alignment_overlay(points, f"{brow_alignment:.0f}%"),
        },
        "nose_deviation_from_centerline": {
            "value": round(nose_dev, 2),
            "value_display": f"{nose_dev:.1f}%",
            "overlay": symmetry_overlay(points, d, f"{nose_dev:.1f}%"),
        },
        "eye_cant": {
            "value": round(eye_tilt, 2),
            "value_display": f"{eye_tilt:.1f}%",
            "overlay": generic_horizontal_ratio_overlay(
                d["left_eye_center"],
                d["right_eye_center"],
                {"x": d["left_eye_center"]["x"], "y": d["left_eye_center"]["y"] + 22},
                {"x": d["right_eye_center"]["x"], "y": d["left_eye_center"]["y"] + 22},
                f"{eye_tilt:.1f}%"
            ),
        },
    }

    return metrics