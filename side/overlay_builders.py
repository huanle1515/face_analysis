from core.overlays import primitives


def _mid(a, b):
    return {
        "x": (float(a["x"]) + float(b["x"])) / 2.0,
        "y": (float(a["y"]) + float(b["y"])) / 2.0,
    }


def projection_overlay(a, b, text):
    mid = _mid(a, b)
    return primitives(
        {
            "type": "segment",
            "p1": a,
            "p2": b,
            "text": text,
            "style": "measurement_primary",
            "label_style": "value_chip",
            "label_x": mid["x"],
            "label_y": mid["y"] - 18,
            "show_dots": True,
        }
    )


def angle_overlay(a, b, c, text):
    return primitives(
        {
            "type": "angle",
            "a": a,
            "b": b,
            "c": c,
            "text": text,
            "style": "angle_arc",
            "ref_style": "reference_line",
            "measure_style": "measurement_primary",
            "label_style": "value_chip",
            "arm_length_a": 42,
            "arm_length_c": 42,
            "radius": 24,
        }
    )


def line_to_reference_overlay(point, ref_a, ref_b, text):
    return primitives(
        {
            "type": "point_to_line",
            "point": point,
            "ref_a": ref_a,
            "ref_b": ref_b,
            "text": text,
            "ref_style": "reference_line",
            "measure_style": "measurement_primary",
            "label_style": "value_chip",
            "segment_start_frac": 0.18,
            "segment_end_frac": 0.80,
        }
    )