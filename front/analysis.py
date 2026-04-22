from front.metrics import compute_front_metrics
from front.definitions import FRONT_METRICS, FRONT_DEFS
from core.scoring import score_from_range, overall_score, classify_layer


def run_front_analysis(base_image, points, derived, pose, quality):
    raw_metrics = compute_front_metrics(points, derived)

    metrics = []

    for metric_key in FRONT_METRICS:
        if metric_key not in raw_metrics:
            continue

        raw = raw_metrics[metric_key]
        meta = FRONT_DEFS[metric_key]

        score = score_from_range(
            value=raw["value"],
            ideal_min=meta["ideal_min"],
            ideal_max=meta["ideal_max"],
            min_bound=meta["min_bound"],
            max_bound=meta["max_bound"],
        )

        layer = classify_layer(
            value=raw["value"],
            ideal_min=meta["ideal_min"],
            ideal_max=meta["ideal_max"],
            min_bound=meta["min_bound"],
            max_bound=meta["max_bound"],
        )

        metrics.append({
            "id": metric_key,
            "name": meta["title"],
            "rank": {
                "index": len(metrics) + 1,
                "total": len(FRONT_METRICS),
            },
            "summary": {
                "value_display": raw["value_display"],
                "score_display": f"{score:.2f}/10",
                "score_normalized": round(score * 10, 2),
                "status": layer,
            },
            "detail": {
                "your_value": {
                    "raw": raw["value"],
                    "display": raw["value_display"],
                    "unit": meta["format"],
                },
                "ideal_range": {
                    "min": meta["ideal_min"],
                    "max": meta["ideal_max"],
                    "display": (
                        f'1:{meta["ideal_min"]}–{meta["ideal_max"]}'
                        if meta["format"] == "ratio_1_to_x"
                        else f'{meta["ideal_min"]}–{meta["ideal_max"]}'
                    ),
                    "unit": meta["format"],
                },
                "score": {
                    "raw_10": score,
                    "normalized_100": round(score * 10, 2),
                    "display": f"{score:.2f}/10",
                },
                "status": layer,
                "about": meta["description"],
                "scale": {
                    "min": meta["min_bound"],
                    "ideal_min": meta["ideal_min"],
                    "ideal_max": meta["ideal_max"],
                    "max": meta["max_bound"],
                    "marker_value": raw["value"],
                    "min_display": str(meta["min_bound"]),
                    "max_display": str(meta["max_bound"]),
                },
                "overlay": raw["overlay"],
            }
        })

    return {
        "analysis_type": "front",
        "overall": {
            "score": overall_score(metrics),
            "label": "Balanced" if overall_score(metrics) >= 80 else "Needs Improvement" if overall_score(metrics) >= 60 else "Low Harmony",
        },
        "metrics": metrics,
        "notes": [
            "Front analysis uses derived landmarks and soft scoring.",
            "Each metric is shown with a layer label: Ideal, Near Ideal, Moderate Deviation, or Strong Deviation.",
        ],
        "diagnostics": {
            "pose": pose,
            "quality": quality,
        },
    }