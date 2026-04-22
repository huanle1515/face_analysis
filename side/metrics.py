from core.geometry import (
    dist,
    horizontal_dist,
    vertical_dist,
    angle3,
    point_to_line_signed_distance,
)
from side.overlay_builders import projection_overlay, line_to_reference_overlay, angle_overlay


def _safe_ratio(num, den, fallback=0.0):
    den = float(den)
    if abs(den) < 1e-6:
        return float(fallback)
    return float(num) / den


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _mean_x(*pts):
    return sum(float(p["x"]) for p in pts) / max(len(pts), 1)


def _mean_y(*pts):
    return sum(float(p["y"]) for p in pts) / max(len(pts), 1)


def _point(x, y):
    return {"x": float(x), "y": float(y)}


def _blend_point(a, b, wa=0.5, wb=0.5):
    s = wa + wb
    return {
        "x": (a["x"] * wa + b["x"] * wb) / s,
        "y": (a["y"] * wa + b["y"] * wb) / s,
    }


def _build_side_stable_points(points, d):
    nose_tip = points["nose_tip"]
    subnasale = d["subnasale_stable"]
    raw_chin = d["chin_stable"]
    columella = points["columella"]
    glabella = points["glabella"]
    forehead = points["forehead_profile"]
    raw_neck = points["cervical_point"]

    upper_lip = points["upper_lip_front"]
    lower_lip = points["lower_lip_front"]

    upper_lip_stable = _point(
        _mean_x(upper_lip, subnasale),
        upper_lip["y"],
    )
    lower_lip_stable = _point(
        _mean_x(lower_lip, raw_chin),
        lower_lip["y"],
    )

    # Stabilize columella/subnasale neighborhood for nasal-base direction
    columella_stable = _point(
        _mean_x(columella, nose_tip, subnasale),
        _mean_y(columella, subnasale),
    )

    glabella_stable = _point(
        _mean_x(glabella, forehead),
        _mean_y(glabella, forehead),
    )

    # New chin stabilization:
    # blend the raw chin with a local lower-face anchor so it does not drift too far forward.
    lower_face_anchor = _point(
        _mean_x(raw_chin, lower_lip_stable, subnasale),
        max(raw_chin["y"], lower_lip_stable["y"] + abs(raw_chin["y"] - lower_lip_stable["y"]) * 0.15),
    )
    chin_stable = _blend_point(raw_chin, lower_face_anchor, wa=0.68, wb=0.32)

    # Stabilize neck point so it sits posterior/inferior to the chin
    neck_stable = _point(
        min(raw_neck["x"], chin_stable["x"] - abs(chin_stable["x"] - subnasale["x"]) * 0.35),
        max(raw_neck["y"], chin_stable["y"] + abs(chin_stable["y"] - subnasale["y"]) * 0.10),
    )

    # Nasal-base direction point: slightly posterior/superior from subnasale toward columella
    nasal_base_ref = _blend_point(columella_stable, subnasale, wa=0.65, wb=0.35)

    # Upper-lip direction point: use a stabilized upper-lip front point with some lower-lip anchoring
    upper_lip_ref = _point(
        _mean_x(upper_lip_stable, lower_lip_stable),
        upper_lip_stable["y"],
    )

    return {
        "nose_tip": nose_tip,
        "subnasale": subnasale,
        "chin": chin_stable,
        "raw_chin": raw_chin,
        "upper_lip": upper_lip_stable,
        "lower_lip": lower_lip_stable,
        "upper_lip_ref": upper_lip_ref,
        "columella": columella_stable,
        "nasal_base_ref": nasal_base_ref,
        "glabella": glabella_stable,
        "forehead": forehead,
        "neck": neck_stable,
        "raw_neck": raw_neck,
    }


def _metric_confidences(points, s):
    face_h = max(vertical_dist(s["forehead"], s["chin"]), 1e-6)
    nose_proj_ratio = horizontal_dist(s["nose_tip"], s["subnasale"]) / face_h
    chin_proj_ratio = horizontal_dist(s["subnasale"], s["chin"]) / face_h
    lip_gap_ratio = vertical_dist(s["upper_lip"], s["lower_lip"]) / face_h
    neck_dx = abs(s["neck"]["x"] - s["chin"]["x"]) / face_h
    neck_dy = abs(s["neck"]["y"] - s["chin"]["y"]) / face_h

    conf = {
        "chin_projection": 1.0,
        "facial_convexity": 1.0,
        "nasolabial_angle": 1.0,
        "jaw_projection": 1.0,
        "neck_chin_angle": 1.0,
        "nose_projection": 1.0,
        "lip_position": 1.0,
    }

    if s["subnasale"]["x"] >= s["nose_tip"]["x"]:
        conf["nose_projection"] -= 0.35
        conf["nasolabial_angle"] -= 0.30
        conf["jaw_projection"] -= 0.25

    if s["glabella"]["x"] >= s["chin"]["x"]:
        conf["facial_convexity"] -= 0.25

    if nose_proj_ratio < 0.035:
        conf["nose_projection"] -= 0.30
        conf["nasolabial_angle"] -= 0.25
        conf["jaw_projection"] -= 0.20
    elif nose_proj_ratio < 0.05:
        conf["nose_projection"] -= 0.12
        conf["nasolabial_angle"] -= 0.12
        conf["jaw_projection"] -= 0.10

    # Stronger chin guards
    if chin_proj_ratio < 0.012:
        conf["chin_projection"] -= 0.30
        conf["jaw_projection"] -= 0.20
        conf["neck_chin_angle"] -= 0.10
    elif chin_proj_ratio < 0.025:
        conf["chin_projection"] -= 0.12
        conf["jaw_projection"] -= 0.10

    if chin_proj_ratio > 0.14:
        conf["chin_projection"] -= 0.35
        conf["jaw_projection"] -= 0.25
    elif chin_proj_ratio > 0.10:
        conf["chin_projection"] -= 0.18

    if lip_gap_ratio < 0.008:
        conf["lip_position"] -= 0.30
        conf["nasolabial_angle"] -= 0.18
    elif lip_gap_ratio < 0.012:
        conf["lip_position"] -= 0.12

    # Nasolabial geometry sanity
    if s["upper_lip"]["y"] <= s["subnasale"]["y"]:
        conf["nasolabial_angle"] -= 0.25
    if s["nasal_base_ref"]["x"] < s["subnasale"]["x"]:
        conf["nasolabial_angle"] -= 0.10

    if neck_dx < 0.03:
        conf["neck_chin_angle"] -= 0.35
    elif neck_dx < 0.05:
        conf["neck_chin_angle"] -= 0.18

    if neck_dy < 0.02:
        conf["neck_chin_angle"] -= 0.35
    elif neck_dy < 0.05:
        conf["neck_chin_angle"] -= 0.18

    balance = _safe_ratio(chin_proj_ratio, max(nose_proj_ratio, 1e-6), fallback=0.0)
    if balance > 1.8:
        conf["jaw_projection"] -= 0.40
    elif balance > 1.4:
        conf["jaw_projection"] -= 0.20

    return {k: round(_clamp(v, 0.0, 1.0), 3) for k, v in conf.items()}


def compute_side_metrics(points, d):
    s = _build_side_stable_points(points, d)

    face_h = max(vertical_dist(s["forehead"], s["chin"]), 1e-6)
    nose_proj_px = horizontal_dist(s["nose_tip"], s["subnasale"])
    chin_proj_px = horizontal_dist(s["subnasale"], s["chin"])

    facial_convexity = angle3(s["glabella"], s["subnasale"], s["chin"])

    # New nasolabial construction:
    # use a stabilized nasal-base direction and a stabilized upper-lip direction.
    nasolabial = angle3(s["nasal_base_ref"], s["subnasale"], s["upper_lip_ref"])

    neck_chin = angle3(s["neck"], s["chin"], s["subnasale"])

    # Softer/bounded chin projection so extreme drift is reduced
    chin_projection_raw = _safe_ratio(chin_proj_px, face_h, fallback=0.0)
    chin_projection = _clamp(chin_projection_raw, 0.0, 0.16)

    nose_projection = _safe_ratio(
        horizontal_dist(s["nose_tip"], s["subnasale"]),
        dist(s["nose_tip"], s["subnasale"]),
        fallback=0.0,
    )

    nose_proj_norm = _safe_ratio(nose_proj_px, face_h, fallback=0.0)
    jaw_projection_raw = _safe_ratio(chin_projection, max(nose_proj_norm, 1e-6), fallback=0.0)
    jaw_projection = _clamp(jaw_projection_raw, 0.0, 1.60)

    lip_signed = point_to_line_signed_distance(s["lower_lip"], s["nose_tip"], s["chin"])
    lip_position = _safe_ratio(lip_signed, face_h, fallback=0.0)

    confidences = _metric_confidences(points, s)

    return {
        "chin_projection": {
            "value": round(chin_projection, 3),
            "value_display": f"{chin_projection:.3f}x",
            "overlay": projection_overlay(s["subnasale"], s["chin"], f"{chin_projection:.3f}x"),
            "confidence": confidences["chin_projection"],
        },
        "facial_convexity": {
            "value": round(facial_convexity, 2),
            "value_display": f"{facial_convexity:.0f}°",
            "overlay": angle_overlay(s["glabella"], s["subnasale"], s["chin"], f"{facial_convexity:.0f}°"),
            "confidence": confidences["facial_convexity"],
        },
        "nasolabial_angle": {
            "value": round(nasolabial, 2),
            "value_display": f"{nasolabial:.0f}°",
            "overlay": angle_overlay(s["nasal_base_ref"], s["subnasale"], s["upper_lip_ref"], f"{nasolabial:.0f}°"),
            "confidence": confidences["nasolabial_angle"],
        },
        "jaw_projection": {
            "value": round(jaw_projection, 2),
            "value_display": f"{jaw_projection:.2f}x",
            "overlay": projection_overlay(s["subnasale"], s["chin"], f"{jaw_projection:.2f}x"),
            "confidence": confidences["jaw_projection"],
        },
        "neck_chin_angle": {
            "value": round(neck_chin, 2),
            "value_display": f"{neck_chin:.0f}°",
            "overlay": angle_overlay(s["neck"], s["chin"], s["subnasale"], f"{neck_chin:.0f}°"),
            "confidence": confidences["neck_chin_angle"],
        },
        "nose_projection": {
            "value": round(nose_projection, 2),
            "value_display": f"{nose_projection:.2f}x",
            "overlay": projection_overlay(s["subnasale"], s["nose_tip"], f"{nose_projection:.2f}x"),
            "confidence": confidences["nose_projection"],
        },
        "lip_position": {
            "value": round(lip_position, 4),
            "value_display": f"{lip_position:.4f}x",
            "overlay": line_to_reference_overlay(s["lower_lip"], s["nose_tip"], s["chin"], f"{lip_position:.4f}x"),
            "confidence": confidences["lip_position"],
        },
    }