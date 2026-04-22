import math
import numpy as np


def point(x: float, y: float):
    return {"x": float(x), "y": float(y)}


def midpoint(a, b):
    return point((a["x"] + b["x"]) / 2.0, (a["y"] + b["y"]) / 2.0)


def mean_point(points):
    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    return point(sum(xs) / len(xs), sum(ys) / len(ys))


def dist(a, b) -> float:
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def horizontal_dist(a, b) -> float:
    return abs(a["x"] - b["x"])


def vertical_dist(a, b) -> float:
    return abs(a["y"] - b["y"])


def angle3(a, b, c) -> float:
    ba = np.array([a["x"] - b["x"], a["y"] - b["y"]], dtype=float)
    bc = np.array([c["x"] - b["x"], c["y"] - b["y"]], dtype=float)
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom == 0:
        return 0.0
    cosang = np.clip(np.dot(ba, bc) / denom, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))


def point_to_line_signed_distance(p0, a, b) -> float:
    ax, ay, bx, by = a["x"], a["y"], b["x"], b["y"]
    px, py = p0["x"], p0["y"]
    den = math.hypot(bx - ax, by - ay)
    if den < 1e-6:
        return 0.0
    return ((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / den


def project_point_to_line(p0, a, b):
    ax, ay = a["x"], a["y"]
    bx, by = b["x"], b["y"]
    px, py = p0["x"], p0["y"]
    abx, aby = bx - ax, by - ay
    ab2 = abx * abx + aby * aby
    if ab2 < 1e-6:
        return point(ax, ay)
    t = ((px - ax) * abx + (py - ay) * aby) / ab2
    return point(ax + t * abx, ay + t * aby)


def line_interpolate(a, b, t: float):
    return point(
        a["x"] + (b["x"] - a["x"]) * t,
        a["y"] + (b["y"] - a["y"]) * t,
    )


def translate(p, dx=0.0, dy=0.0):
    return point(p["x"] + dx, p["y"] + dy)