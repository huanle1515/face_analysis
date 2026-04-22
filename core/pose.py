from core.geometry import horizontal_dist, vertical_dist, midpoint


def estimate_front_pose(pts):
    eye_line_left = midpoint(pts["left_eye_outer"], pts["left_eye_inner"])
    eye_line_right = midpoint(pts["right_eye_outer"], pts["right_eye_inner"])
    mouth_mid = midpoint(pts["mouth_left"], pts["mouth_right"])

    eye_tilt_px = float(eye_line_right["y"] - eye_line_left["y"])
    face_w = max(float(horizontal_dist(pts["left_face"], pts["right_face"])), 1e-6)
    roll_ratio = abs(eye_tilt_px) / face_w

    nose_center_offset = abs(float(pts["nose_tip"]["x"] - mouth_mid["x"])) / face_w

    return {
        "roll_ratio": round(float(roll_ratio), 4),
        "center_offset_ratio": round(float(nose_center_offset), 4),
        "is_front_acceptable": bool(roll_ratio < 0.05 and nose_center_offset < 0.12),
    }


def estimate_side_pose(pts):
    eye_width = float(horizontal_dist(pts["left_eye_outer"], pts["left_eye_inner"]))
    other_eye_width = float(horizontal_dist(pts["right_eye_outer"], pts["right_eye_inner"]))
    dominance = max(eye_width, other_eye_width) / max(min(eye_width, other_eye_width), 1e-6)

    nose_proj = abs(float(pts["nose_tip"]["x"] - pts["subnasale"]["x"]))
    face_h = max(float(vertical_dist(pts["top"], pts["chin"])), 1e-6)
    nose_projection_ratio = nose_proj / face_h

    return {
        "eye_dominance_ratio": round(float(dominance), 3),
        "nose_projection_ratio": round(float(nose_projection_ratio), 4),
        "is_side_acceptable": bool(dominance > 1.2 or nose_projection_ratio > 0.05),
    }