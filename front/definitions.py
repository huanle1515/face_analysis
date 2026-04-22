FRONT_METRICS = [
    "facial_width_to_height_ratio",
    "facial_symmetry",
    "eye_spacing_ratio",
    "jaw_width",
    "lip_ratio",
    "nose_width_ratio",
    "brow_alignment",
    "nose_deviation_from_centerline",
    "eye_cant"
]

FRONT_DEFS = {
    "facial_width_to_height_ratio": {
        "title": "Facial Width to Height Ratio",
        "short_label": "Facial Width to Height Ratio",
        "ideal_min": 1.25,
        "ideal_max": 1.40,
        "min_bound": 1.00,
        "max_bound": 1.70,
        "format": "ratio",
        "description": (
            "This is the vertical distance from top_stable to chin_stable divided by the horizontal distance "
            "between left_face_stable and right_face_stable."
        ),
        "weight": 1.0,
    },
    "facial_symmetry": {
        "title": "Facial Symmetry",
        "short_label": "Facial Symmetry",
        "ideal_min": 88.0,
        "ideal_max": 100.0,
        "min_bound": 50.0,
        "max_bound": 100.0,
        "format": "percent",
        "description": (
            "This is computed from the average horizontal offset of the nose tip, mouth center, and eye midpoint "
            "from the face centerline, then converted into a percentage score relative to face width."
        ),
        "weight": 1.0,
    },
    "eye_spacing_ratio": {
        "title": "Eye Spacing Ratio",
        "short_label": "Eye Spacing Ratio",
        "ideal_min": 46.4,
        "ideal_max": 47.5,
        "min_bound": 38.1,
        "max_bound": 55.8,
        "format": "percent",
        "description": (
            "This is the horizontal distance between the left and right eye centers, divided by stable face width "
            "with the current calibration factor, then expressed as a percentage."
        ),
        "weight": 1.0,
    },
    "jaw_width": {
        "title": "Jaw Width",
        "short_label": "Jaw Width",
        "ideal_min": 0.78,
        "ideal_max": 0.86,
        "min_bound": 0.60,
        "max_bound": 0.98,
        "format": "ratio",
        "description": (
            "This is the horizontal distance between left_jaw_stable and right_jaw_stable, multiplied by 0.95, "
            "then divided by stable face width."
        ),
        "weight": 1.0,
    },
    "lip_ratio": {
        "title": "Lip Ratio",
        "short_label": "Lip Ratio",
        "ideal_min": 1.45,
        "ideal_max": 1.75,
        "min_bound": 1.10,
        "max_bound": 2.20,
        "format": "ratio_1_to_x",
        "description": (
            "This is the vertical height of the lower lip divided by the vertical height of the upper lip, "
            "using the current upper and lower lip landmark pairs."
        ),
        "weight": 1.0,
    },
    "nose_width_ratio": {
        "title": "Nose Width Ratio",
        "short_label": "Nose Width Ratio",
        "ideal_min": 0.18,
        "ideal_max": 0.24,
        "min_bound": 0.12,
        "max_bound": 0.33,
        "format": "ratio",
        "description": (
            "This is the horizontal distance between the current nose-width anchor points, multiplied by 0.88, "
            "then divided by stable face width."
        ),
        "weight": 1.0,
    },
    "brow_alignment": {
        "title": "Brow Alignment",
        "short_label": "Brow Alignment",
        "ideal_min": 90.0,
        "ideal_max": 100.0,
        "min_bound": 50.0,
        "max_bound": 100.0,
        "format": "percent",
        "description": (
            "This is based on the vertical difference between left_brow_mid and right_brow_mid, normalized by face height, "
            "then converted into a percentage score."
        ),
        "weight": 1.0,
    },
    "nose_deviation_from_centerline": {
        "title": "Nose Deviation from Centerline",
        "short_label": "Nose Deviation from Centerline",
        "ideal_min": 0.0,
        "ideal_max": 1.0,
        "min_bound": 0.0,
        "max_bound": 5.0,
        "format": "percent",
        "description": (
            "This is the horizontal distance between the nose tip and the face centerline, "
            "divided by stable face width with the current scaling factor, then expressed as a percentage."
        ),
        "weight": 1.0,
    },
    "eye_cant": {
        "title": "Eye Cant",
        "short_label": "Eye Cant",
        "ideal_min": 0.0,
        "ideal_max": 1.0,
        "min_bound": 0.0,
        "max_bound": 5.0,
        "format": "percent",
        "description": (
            "This is the vertical difference between the right and left eye centers, "
            "divided by stable face width, then expressed as a percentage."
        ),
        "weight": 1.0,
    },
}
