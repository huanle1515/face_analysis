import math
from core.geometry import point


def rotate_point(p, center, angle_rad):
    x = p["x"] - center["x"]
    y = p["y"] - center["y"]
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    xr = x * c - y * s
    yr = x * s + y * c
    return point(xr + center["x"], yr + center["y"])


def is_point_dict(value):
    return isinstance(value, dict) and "x" in value and "y" in value


def normalize_front_points(points, derived):
    left_eye = derived["left_eye_center"]
    right_eye = derived["right_eye_center"]

    dx = right_eye["x"] - left_eye["x"]
    dy = right_eye["y"] - left_eye["y"]
    angle = math.atan2(dy, dx)

    center = point(
        (left_eye["x"] + right_eye["x"]) / 2.0,
        (left_eye["y"] + right_eye["y"]) / 2.0
    )

    rotated_points = {
        k: rotate_point(v, center, -angle)
        for k, v in points.items()
    }

    rotated_derived = {}
    for k, v in derived.items():
        if is_point_dict(v):
            rotated_derived[k] = rotate_point(v, center, -angle)
        else:
            rotated_derived[k] = v

    # recompute centerline-dependent derived values after rotation
    if "left_face_stable" in rotated_derived and "right_face_stable" in rotated_derived:
        face_center_x = (
            rotated_derived["left_face_stable"]["x"] +
            rotated_derived["right_face_stable"]["x"]
        ) / 2.0
        rotated_derived["face_center_x"] = face_center_x

        if "top_stable" in rotated_derived and "chin_stable" in rotated_derived:
            rotated_derived["face_midline_top"] = point(
                face_center_x,
                rotated_derived["top_stable"]["y"]
            )
            rotated_derived["face_midline_bottom"] = point(
                face_center_x,
                rotated_derived["chin_stable"]["y"]
            )

    return rotated_points, rotated_derived, math.degrees(angle)