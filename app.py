from flask import Flask, jsonify, request, send_from_directory
import os
import math

import numpy as np

from core.detector import LandmarkDetector, crop_face, collect_named_points
from core.derived_points import build_front_derived_points, build_side_derived_points
from core.pose import estimate_front_pose, estimate_side_pose
from core.quality import assess_image_quality
from core.overlay_renderer import render_overlay_image, encode_bgr_to_data_uri

from front.analysis import run_front_analysis
from side.analysis import run_side_analysis

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.join(BASE_DIR, "models", "face_landmarker.task"),
)

app = Flask(__name__, static_folder=None)
detector = LandmarkDetector(model_path=MODEL_PATH)


def safe_num(x, default=0.0):
    if x is None:
        return default
    if isinstance(x, (float, np.floating)) and (math.isnan(float(x)) or math.isinf(float(x))):
        return default
    return x


def parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def sanitize_metrics(metrics):
    if isinstance(metrics, dict):
        for _, metric in metrics.items():
            if not isinstance(metric, dict):
                continue

            metric["value"] = safe_num(metric.get("value"), 0.0)
            metric["score"] = safe_num(metric.get("score"), 0.0)

            if not metric.get("value_display"):
                metric["value_display"] = str(metric["value"])

            if not metric.get("status"):
                metric["status"] = "Unknown"

            if not metric.get("description"):
                metric["description"] = ""

        return metrics

    if isinstance(metrics, list):
        for metric in metrics:
            if not isinstance(metric, dict):
                continue

            if "summary" in metric and isinstance(metric["summary"], dict):
                metric["summary"]["score_normalized"] = safe_num(
                    metric["summary"].get("score_normalized"), 0.0
                )

            if "detail" in metric and isinstance(metric["detail"], dict):
                your_value = metric["detail"].get("your_value", {})
                score = metric["detail"].get("score", {})

                if isinstance(your_value, dict):
                    your_value["raw"] = safe_num(your_value.get("raw"), 0.0)

                if isinstance(score, dict):
                    score["raw_10"] = safe_num(score.get("raw_10"), 0.0)
                    score["normalized_100"] = safe_num(score.get("normalized_100"), 0.0)

        return metrics

    return metrics


def attach_metric_overlay_images(metrics, crop_img, include_images=True, include_overlay_data=True):
    if not isinstance(metrics, list):
        return metrics

    for metric in metrics:
        if not isinstance(metric, dict):
            continue

        detail = metric.get("detail")
        if not isinstance(detail, dict):
            continue

        overlay = detail.get("overlay")
        if not overlay:
            detail["overlay_image"] = None
            if not include_overlay_data and "overlay" in detail:
                detail.pop("overlay", None)
            continue

        if include_images:
            try:
                annotated = render_overlay_image(crop_img, overlay)
                detail["overlay_image"] = encode_bgr_to_data_uri(annotated)
            except Exception:
                detail["overlay_image"] = None
        else:
            detail["overlay_image"] = None

        if not include_overlay_data:
            detail.pop("overlay", None)

    return metrics


def to_json_safe(obj):
    if isinstance(obj, dict):
        return {str(k): to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_json_safe(v) for v in obj]
    if isinstance(obj, tuple):
        return [to_json_safe(v) for v in obj]
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        val = float(obj)
        if math.isnan(val) or math.isinf(val):
            return 0.0
        return val
    return obj


def build_image_payload(crop_img, include_base_image=True):
    payload = {
        "width": int(crop_img.shape[1]),
        "height": int(crop_img.shape[0]),
    }
    payload["base_image"] = encode_bgr_to_data_uri(crop_img) if include_base_image else None
    return payload


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "face-harmony-system",
        "model_path": MODEL_PATH,
    })


@app.route("/analyze/front", methods=["POST"])
def analyze_front():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    include_overlay_images = parse_bool(request.args.get("include_overlay_images"), True)
    include_overlay_data = parse_bool(request.args.get("include_overlay_data"), True)
    include_base_image = parse_bool(request.args.get("include_base_image"), True)

    file = request.files["file"]
    img_bytes = file.read()

    try:
        img, landmarks, width, height = detector.detect(img_bytes)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Front detection failed: {str(e)}"}), 500

    try:
        quality = assess_image_quality(img)
        crop_img, offset = crop_face(img, landmarks)
        points = collect_named_points(landmarks, width, height, offset)
        pose = estimate_front_pose(points)
        derived = build_front_derived_points(points)

        result = run_front_analysis(
            base_image=crop_img,
            points=points,
            derived=derived,
            pose=pose,
            quality=quality,
        )

        if isinstance(result, dict) and "metrics" in result:
            result["metrics"] = sanitize_metrics(result["metrics"])
            result["metrics"] = attach_metric_overlay_images(
                result["metrics"],
                crop_img,
                include_images=include_overlay_images,
                include_overlay_data=include_overlay_data,
            )

        result["image"] = build_image_payload(
            crop_img,
            include_base_image=include_base_image,
        )

        return jsonify(to_json_safe(result))

    except Exception as e:
        return jsonify({"error": f"Front analysis failed: {str(e)}"}), 500


@app.route("/analyze/side", methods=["POST"])
def analyze_side():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    include_overlay_images = parse_bool(request.args.get("include_overlay_images"), True)
    include_overlay_data = parse_bool(request.args.get("include_overlay_data"), True)
    include_base_image = parse_bool(request.args.get("include_base_image"), True)

    file = request.files["file"]
    img_bytes = file.read()

    try:
        img, landmarks, width, height = detector.detect_with_fallbacks(img_bytes)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Side detection failed: {str(e)}"}), 500

    try:
        quality = assess_image_quality(img)
        crop_img, offset = crop_face(img, landmarks)
        points = collect_named_points(landmarks, width, height, offset)
        pose = estimate_side_pose(points)
        derived = build_side_derived_points(points)

        result = run_side_analysis(
            base_image=crop_img,
            points=points,
            derived=derived,
            pose=pose,
            quality=quality,
        )

        if isinstance(result, dict) and "metrics" in result:
            result["metrics"] = sanitize_metrics(result["metrics"])
            result["metrics"] = attach_metric_overlay_images(
                result["metrics"],
                crop_img,
                include_images=include_overlay_images,
                include_overlay_data=include_overlay_data,
            )

        result["image"] = build_image_payload(
            crop_img,
            include_base_image=include_base_image,
        )

        return jsonify(to_json_safe(result))

    except Exception as e:
        return jsonify({"error": f"Side analysis failed: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)