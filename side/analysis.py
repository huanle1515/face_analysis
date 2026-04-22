from core.scoring import score_from_range, overall_score, classify_layer
from side.definitions import SIDE_METRICS, SIDE_DEFS
from side.validators import validate_side_inputs
from side.metrics import compute_side_metrics


MIN_METRIC_CONFIDENCE = 0.55


def run_side_analysis(base_image, points, derived, pose, quality):
    issues = validate_side_inputs(pose, quality)
    raw = compute_side_metrics(points, derived)

    metrics = []

    for metric_id in SIDE_METRICS:
        meta = SIDE_DEFS[metric_id]
        item = raw[metric_id]
        confidence = float(item.get("confidence", 1.0))

        score_10 = score_from_range(
            item["value"],
            meta["ideal_min"],
            meta["ideal_max"],
            meta["scale_min"],
            meta["scale_max"],
        )
        score_100 = round(score_10 * 10.0, 2)

        layer = classify_layer(
            value=item["value"],
            ideal_min=meta["ideal_min"],
            ideal_max=meta["ideal_max"],
            min_bound=meta["scale_min"],
            max_bound=meta["scale_max"],
        )

        metrics.append({
            "id": metric_id,
            "weight": meta["weight"],
            "rank": {
                "index": len(metrics) + 1,
                "total": len(SIDE_METRICS),
            },
            "name": meta["name"],
            "summary": {
                "value_display": item["value_display"],
                "score_display": f"{score_10:.2f}/10",
                "score_normalized": score_100,
                "status": layer,
                "confidence_display": f"{confidence * 100:.0f}%",
            },
            "detail": {
                "your_value": {
                    "raw": item["value"],
                    "display": item["value_display"],
                    "unit": meta["unit"],
                },
                "ideal_range": {
                    "min": meta["ideal_min"],
                    "max": meta["ideal_max"],
                    "display": meta["ideal_display"],
                    "unit": meta["unit"],
                },
                "score": {
                    "raw_10": score_10,
                    "normalized_100": score_100,
                    "display": f"{score_10:.2f}/10",
                },
                "status": layer,
                "about": meta["about"],
                "confidence": {
                    "raw": confidence,
                    "display": f"{confidence * 100:.0f}%",
                    "min_required": f"{MIN_METRIC_CONFIDENCE * 100:.0f}%",
                },
                "scale": {
                    "min": meta["scale_min"],
                    "ideal_min": meta["ideal_min"],
                    "ideal_max": meta["ideal_max"],
                    "max": meta["scale_max"],
                    "marker_value": item["value"],
                    "min_display": meta["scale_min_display"],
                    "max_display": meta["scale_max_display"],
                },
                "overlay": item["overlay"],
            },
        })

    notes = [
        "Side analysis shows all available metrics, even when confidence is low.",
        "Confidence is still reported so you can judge how reliable each side measurement may be.",
        "Each metric is shown with a layer label: Ideal, Near Ideal, Moderate Deviation, or Strong Deviation.",
        "All side metrics are 2D estimates and are normalized for photo robustness where possible.",
        *issues,
    ]

    if not metrics:
        notes.append("No side metrics could be generated for this image.")
        return {
            "analysis_type": "side",
            "overall": {
                "score": 0,
                "label": "Insufficient Data",
            },
            "metrics": [],
            "hidden_metrics": [],
            "notes": notes,
            "diagnostics": {
                "pose": pose,
                "quality": quality,
            },
        }

    overall = overall_score(metrics)

    return {
        "analysis_type": "side",
        "overall": {
            "score": overall,
            "label": (
                "Balanced Profile" if overall >= 80 else
                "Moderately Balanced" if overall >= 65 else
                "Needs Improvement"
            ),
        },
        "metrics": metrics,
        "hidden_metrics": [],
        "notes": notes,
        "diagnostics": {
            "pose": pose,
            "quality": quality,
        },
    }