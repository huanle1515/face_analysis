def score_by_range(value, ideal_min, ideal_max, min_bound=None, max_bound=None):
    if value is None:
        return 0.0

    span = max(ideal_max - ideal_min, 1e-6)

    if min_bound is None:
        min_bound = ideal_min - span * 2.0

    if max_bound is None:
        max_bound = ideal_max + span * 2.0

    if ideal_min <= value <= ideal_max:
        center = (ideal_min + ideal_max) / 2.0
        half = max(span / 2.0, 1e-6)
        dist = abs(value - center) / half
        score = 10.0 - dist * 1.0
        return round(max(9.0, min(10.0, score)), 2)

    if value < ideal_min:
        dist = (ideal_min - value) / max(ideal_min - min_bound, 1e-6)
        score = 9.0 - dist * 6.0
        return round(max(2.5, min(8.99, score)), 2)

    dist = (value - ideal_max) / max(max_bound - ideal_max, 1e-6)
    score = 9.0 - dist * 6.0
    return round(max(2.5, min(8.99, score)), 2)


def score_from_range(value, ideal_min, ideal_max, min_bound=None, max_bound=None):
    return score_by_range(value, ideal_min, ideal_max, min_bound, max_bound)


def classify_layer(value, ideal_min, ideal_max, min_bound=None, max_bound=None):
    """
    Returns a softer user-facing label:

    - Ideal
    - Near Ideal
    - Moderate Deviation
    - Strong Deviation

    Classification is based on how far the value is outside the ideal range,
    normalized to the available scale on that side.
    """
    if value is None:
        return "Unknown"

    span = max(ideal_max - ideal_min, 1e-6)

    if min_bound is None:
        min_bound = ideal_min - span * 2.0

    if max_bound is None:
        max_bound = ideal_max + span * 2.0

    if ideal_min <= value <= ideal_max:
        return "Ideal"

    if value < ideal_min:
        side_span = max(ideal_min - min_bound, 1e-6)
        ratio = (ideal_min - value) / side_span
    else:
        side_span = max(max_bound - ideal_max, 1e-6)
        ratio = (value - ideal_max) / side_span

    if ratio <= 0.33:
        return "Near Ideal"
    if ratio <= 0.66:
        return "Moderate Deviation"
    return "Strong Deviation"


def classify_range(value, ideal_min, ideal_max, min_bound=None, max_bound=None):
    # Backward-compatible alias
    return classify_layer(value, ideal_min, ideal_max, min_bound, max_bound)


def overall_score(metrics):
    """
    Expects metric dicts using metric["summary"]["score_normalized"].
    Supports optional metric["weight"].

    score_normalized should be in 0-100 units.
    """
    if not metrics:
        return 0

    weighted_total = 0.0
    total_weight = 0.0

    for metric in metrics:
        try:
            score = float(metric["summary"]["score_normalized"])
        except Exception:
            continue

        try:
            weight = float(metric.get("weight", 1.0))
        except Exception:
            weight = 1.0

        weight = max(weight, 0.0)
        if weight == 0.0:
            continue

        weighted_total += score * weight
        total_weight += weight

    if total_weight <= 0.0:
        return 0

    return round(weighted_total / total_weight)