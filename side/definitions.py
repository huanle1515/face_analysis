SIDE_DEFS = {
    "chin_projection": {
        "rank": 1,
        "name": "Chin Projection",
        "unit": "x",
        "ideal_min": 0.035,
        "ideal_max": 0.085,
        "ideal_display": "0.035–0.085x",
        "scale_min": 0.00,
        "scale_max": 0.16,
        "scale_min_display": "0.00",
        "scale_max_display": "0.16",
        "about": (
            "This measures the straight-line distance between the stabilized subnasale point "
            "and the stabilized chin point, normalized by profile height. It is a 2D distance ratio "
            "based on the side photo."
        ),
        "weight": 1.0,
    },
    "facial_convexity": {
        "rank": 2,
        "name": "Facial Convexity",
        "unit": "°",
        "ideal_min": 160.0,
        "ideal_max": 172.0,
        "ideal_display": "160–172°",
        "scale_min": 148.0,
        "scale_max": 180.0,
        "scale_min_display": "148",
        "scale_max_display": "180",
        "about": (
            "This is the angle formed by the stabilized glabella point, the stabilized subnasale point, "
            "and the stabilized chin point. It measures the profile angle at subnasale in the side view."
        ),
        "weight": 1.2,
    },
    "nasolabial_angle": {
        "rank": 3,
        "name": "Nasolabial Angle",
        "unit": "°",
        "ideal_min": 88.0,
        "ideal_max": 112.0,
        "ideal_display": "88–112°",
        "scale_min": 75.0,
        "scale_max": 125.0,
        "scale_min_display": "75",
        "scale_max_display": "125",
        "about": (
            "This is the angle formed by the stabilized nasal-base reference point, the stabilized subnasale point, "
            "and the stabilized upper-lip reference point. It measures the angle at subnasale using the current "
            "stabilized nose-base and upper-lip construction."
        ),
        "weight": 0.95,
    },
    "jaw_projection": {
        "rank": 4,
        "name": "Jaw Projection",
        "unit": "x",
        "ideal_min": 0.65,
        "ideal_max": 1.10,
        "ideal_display": "0.65–1.10x",
        "scale_min": 0.35,
        "scale_max": 1.60,
        "scale_min_display": "0.35",
        "scale_max_display": "1.60",
        "about": (
            "This is the ratio of chin_projection to normalized nose width in the side view. "
            "Specifically, it divides the normalized subnasale-to-chin distance by the normalized "
            "horizontal nose-tip-to-subnasale distance."
        ),
        "weight": 0.95,
    },
    "neck_chin_angle": {
        "rank": 5,
        "name": "Neck-Chin Angle",
        "unit": "°",
        "ideal_min": 98.0,
        "ideal_max": 122.0,
        "ideal_display": "98–122°",
        "scale_min": 85.0,
        "scale_max": 140.0,
        "scale_min_display": "85",
        "scale_max_display": "140",
        "about": (
            "This is the angle formed by the stabilized neck point, the stabilized chin point, "
            "and the stabilized subnasale point. It measures the angle at the chin using those "
            "three current side-profile landmarks."
        ),
        "weight": 0.8,
    },
    "nose_projection": {
        "rank": 6,
        "name": "Nose Projection",
        "unit": "x",
        "ideal_min": 0.55,
        "ideal_max": 0.82,
        "ideal_display": "0.55–0.82x",
        "scale_min": 0.35,
        "scale_max": 1.00,
        "scale_min_display": "0.35",
        "scale_max_display": "1.00",
        "about": (
            "This is the horizontal distance between the nose tip and the stabilized subnasale point "
            "divided by their full straight-line distance. It measures how horizontally oriented that "
            "nose-tip to subnasale segment is in the side photo."
        ),
        "weight": 1.1,
    },
    "lip_position": {
        "rank": 7,
        "name": "Lip Position",
        "unit": "x",
        "ideal_min": -0.015,
        "ideal_max": 0.008,
        "ideal_display": "-0.015–0.008x",
        "scale_min": -0.050,
        "scale_max": 0.035,
        "scale_min_display": "-0.050",
        "scale_max_display": "0.035",
        "about": (
            "This is the signed perpendicular distance from the stabilized lower-lip point "
            "to the line between the nose tip and the stabilized chin point, normalized by profile height. "
            "Positive and negative values depend on which side of that reference line the lower lip falls."
        ),
        "weight": 0.95,
    },
}