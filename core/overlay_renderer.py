import base64
import math
from typing import Dict, Any, Tuple, Optional

import cv2
import numpy as np


STYLE_MAP = {
    "measurement_primary": {"color": (210, 204, 88), "thickness": 3},
    "reference_line": {"color": (255, 255, 255), "thickness": 2},
    "construction_line": {"color": (215, 208, 199), "thickness": 1},
    "endpoint_dot": {"fill": (222, 222, 248), "stroke": (255, 255, 255), "radius": 5},
    "value_chip": {"fill": (210, 204, 89), "text": (255, 255, 255)},
    "angle_arc": {"color": (210, 204, 89), "thickness": 2},
}


def encode_bgr_to_data_uri(img_bgr: np.ndarray) -> str:
    ok, buf = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not ok:
        raise RuntimeError("Could not encode overlay image")
    return "data:image/jpeg;base64," + base64.b64encode(buf).decode("utf-8")


def _pt(p: Dict[str, float]) -> Tuple[int, int]:
    return int(round(float(p["x"]))), int(round(float(p["y"])))


def _style(name: str) -> Dict[str, Any]:
    return STYLE_MAP.get(name, STYLE_MAP["measurement_primary"])


def _norm(dx: float, dy: float) -> Tuple[float, float, float]:
    d = math.hypot(dx, dy)
    if d < 1e-6:
        return 0.0, 0.0, 1.0
    return dx / d, dy / d, d


def _point_toward(a: Dict[str, float], b: Dict[str, float], length: float) -> Dict[str, float]:
    dx = float(b["x"]) - float(a["x"])
    dy = float(b["y"]) - float(a["y"])
    ux, uy, _ = _norm(dx, dy)
    return {"x": float(a["x"]) + ux * length, "y": float(a["y"]) + uy * length}


def _point_lerp(a: Dict[str, float], b: Dict[str, float], t: float) -> Dict[str, float]:
    return {
        "x": float(a["x"]) + (float(b["x"]) - float(a["x"])) * t,
        "y": float(a["y"]) + (float(b["y"]) - float(a["y"])) * t,
    }


def _draw_line(img: np.ndarray, p1: Dict[str, float], p2: Dict[str, float], style_name: str) -> None:
    s = _style(style_name)
    cv2.line(img, _pt(p1), _pt(p2), s["color"], s["thickness"], cv2.LINE_AA)


def _draw_dot(img: np.ndarray, p: Dict[str, float], style_name: str = "endpoint_dot") -> None:
    s = _style(style_name)
    center = _pt(p)
    cv2.circle(img, center, s.get("radius", 5), s.get("fill", (255, 255, 255)), -1, cv2.LINE_AA)
    cv2.circle(img, center, s.get("radius", 5), s.get("stroke", (255, 255, 255)), 1, cv2.LINE_AA)


def _draw_label(img: np.ndarray, x: float, y: float, text: str, style_name: str = "value_chip") -> None:
    s = _style(style_name)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.62
    thickness = 2

    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    pad_x, pad_y = 12, 8
    x1 = int(round(x - (tw + pad_x * 2) / 2))
    y1 = int(round(y - (th + pad_y * 2) / 2))
    x2 = x1 + tw + pad_x * 2
    y2 = y1 + th + pad_y * 2

    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), s["fill"], -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.95, img, 0.05, 0, img)

    text_x = x1 + pad_x
    text_y = y2 - pad_y - baseline + 1
    cv2.putText(img, text, (text_x, text_y), font, scale, s["text"], thickness, cv2.LINE_AA)


def _draw_angle_compact(img: np.ndarray, item: Dict[str, Any]) -> None:
    a = item["a"]
    b = item["b"]
    c = item["c"]

    arm_a = float(item.get("arm_length_a", 44))
    arm_c = float(item.get("arm_length_c", 44))
    radius = int(round(float(item.get("radius", 24))))

    a_short = _point_toward(b, a, arm_a)
    c_short = _point_toward(b, c, arm_c)

    _draw_line(img, b, a_short, item.get("ref_style", "reference_line"))
    _draw_line(img, b, c_short, item.get("measure_style", "measurement_primary"))

    bx, by = float(b["x"]), float(b["y"])
    ang1 = math.degrees(math.atan2(float(a_short["y"]) - by, float(a_short["x"]) - bx))
    ang2 = math.degrees(math.atan2(float(c_short["y"]) - by, float(c_short["x"]) - bx))

    start = ang1
    end = ang2
    while end - start > 180:
        end -= 360
    while start - end > 180:
        start -= 360

    s = _style(item.get("style", "angle_arc"))
    cv2.ellipse(
        img,
        (int(round(bx)), int(round(by))),
        (radius, radius),
        0,
        start,
        end,
        s["color"],
        s["thickness"],
        cv2.LINE_AA,
    )

    mid = math.radians((start + end) / 2.0)
    label_r = radius + 22
    lx = item.get("label_x", bx + math.cos(mid) * label_r)
    ly = item.get("label_y", by + math.sin(mid) * label_r - 2)
    _draw_label(img, lx, ly, item["text"], item.get("label_style", "value_chip"))


def _draw_segment_compact(img: np.ndarray, item: Dict[str, Any]) -> None:
    p1 = item["p1"]
    p2 = item["p2"]
    _draw_line(img, p1, p2, item.get("style", "measurement_primary"))

    if item.get("show_dots", True):
        _draw_dot(img, p1)
        _draw_dot(img, p2)

    if item.get("text"):
        mx = item.get("label_x", (float(p1["x"]) + float(p2["x"])) / 2.0)
        my = item.get("label_y", (float(p1["y"]) + float(p2["y"])) / 2.0 - 18.0)
        _draw_label(img, mx, my, item["text"], item.get("label_style", "value_chip"))


def _draw_point_to_line_compact(img: np.ndarray, item: Dict[str, Any]) -> None:
    point = item["point"]
    ref_a = item["ref_a"]
    ref_b = item["ref_b"]

    t1 = float(item.get("segment_start_frac", 0.18))
    t2 = float(item.get("segment_end_frac", 0.80))
    seg_a = _point_lerp(ref_a, ref_b, t1)
    seg_b = _point_lerp(ref_a, ref_b, t2)

    ax, ay = float(seg_a["x"]), float(seg_a["y"])
    bx, by = float(seg_b["x"]), float(seg_b["y"])
    px, py = float(point["x"]), float(point["y"])

    abx, aby = bx - ax, by - ay
    ab2 = abx * abx + aby * aby
    if ab2 < 1e-6:
        foot = {"x": ax, "y": ay}
    else:
        t = ((px - ax) * abx + (py - ay) * aby) / ab2
        t = max(0.0, min(1.0, t))
        foot = {"x": ax + abx * t, "y": ay + aby * t}

    _draw_line(img, seg_a, seg_b, item.get("ref_style", "reference_line"))
    _draw_line(img, point, foot, item.get("measure_style", "measurement_primary"))
    _draw_dot(img, point)
    _draw_dot(img, foot)

    lx = item.get("label_x", (px + float(foot["x"])) / 2.0 + 10.0)
    ly = item.get("label_y", (py + float(foot["y"])) / 2.0 - 6.0)
    _draw_label(img, lx, ly, item["text"], item.get("label_style", "value_chip"))


def render_overlay_image(
    base_image_bgr: np.ndarray,
    overlay: Optional[Dict[str, Any]],
) -> np.ndarray:
    out = base_image_bgr.copy()
    if not overlay or "primitives" not in overlay:
        return out

    for item in overlay["primitives"]:
        t = item.get("type")
        if t == "line":
            _draw_line(out, item["p1"], item["p2"], item.get("style", "measurement_primary"))
        elif t == "dot":
            _draw_dot(out, {"x": item["x"], "y": item["y"]}, item.get("style", "endpoint_dot"))
        elif t == "label":
            _draw_label(out, item["x"], item["y"], item["text"], item.get("style", "value_chip"))
        elif t == "angle":
            _draw_angle_compact(out, item)
        elif t == "segment":
            _draw_segment_compact(out, item)
        elif t == "point_to_line":
            _draw_point_to_line_compact(out, item)

    return out