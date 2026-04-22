from core.overlays import line, dot, label, primitives


def eye_spacing_overlay(d, value_display):
    left = d["left_eye_center"]
    right = d["right_eye_center"]
    y_ref = (left["y"] + right["y"]) / 2 + 22
    return primitives(
        line(left, right, "measurement_primary"),
        line(
            {"x": d["left_face_stable"]["x"], "y": y_ref},
            {"x": d["right_face_stable"]["x"], "y": y_ref},
            "reference_line",
        ),
        dot(left),
        dot(right),
        label((left["x"] + right["x"]) / 2, left["y"] - 18, value_display, "value_chip"),
    )


def width_height_overlay(d, value_display):
    top = d["top_stable"]
    bottom = d["chin_stable"]
    left = {"x": d["left_face_stable"]["x"], "y": (top["y"] + bottom["y"]) / 2}
    right = {"x": d["right_face_stable"]["x"], "y": (top["y"] + bottom["y"]) / 2}
    center_x = d["face_center_x"]
    return primitives(
        line({"x": center_x, "y": top["y"]}, {"x": center_x, "y": bottom["y"]}, "measurement_primary"),
        line(left, right, "reference_line"),
        dot({"x": center_x, "y": top["y"]}),
        dot({"x": center_x, "y": bottom["y"]}),
        dot(left),
        dot(right),
        label(center_x + 42, (top["y"] + bottom["y"]) / 2 - 10, value_display, "value_chip"),
    )


def nose_width_overlay(points, d, value_display):
    left = points["nose_left"]
    right = points["nose_right"]
    y_ref = (left["y"] + right["y"]) / 2 + 24
    return primitives(
        line(left, right, "measurement_primary"),
        line(
            {"x": d["left_face_stable"]["x"], "y": y_ref},
            {"x": d["right_face_stable"]["x"], "y": y_ref},
            "reference_line",
        ),
        dot(left),
        dot(right),
        label((left["x"] + right["x"]) / 2, left["y"] - 18, value_display, "value_chip"),
    )


def lower_third_overlay(d, value_display):
    sn = d["subnasale_stable"]
    chin = d["chin_stable"]
    full_x = d["face_center_x"] + 34
    main_x = d["face_center_x"]
    return primitives(
        line({"x": main_x, "y": sn["y"]}, {"x": main_x, "y": chin["y"]}, "measurement_primary"),
        line({"x": full_x, "y": d["top_stable"]["y"]}, {"x": full_x, "y": chin["y"]}, "reference_line"),
        dot({"x": main_x, "y": sn["y"]}),
        dot({"x": main_x, "y": chin["y"]}),
        label(main_x + 54, (sn["y"] + chin["y"]) / 2, value_display, "value_chip"),
    )


def symmetry_overlay(points, d, value_display):
    center_x = d["face_center_x"]
    top_y = d["top_stable"]["y"]
    bottom_y = d["chin_stable"]["y"]
    mouth = d["mouth_center"]
    return primitives(
        line({"x": center_x, "y": top_y}, {"x": center_x, "y": bottom_y}, "measurement_primary"),
        line(d["left_eye_center"], d["right_eye_center"], "reference_line"),
        line(points["mouth_left"], points["mouth_right"], "construction_line"),
        dot(points["nose_tip"]),
        dot(mouth),
        label(center_x + 46, top_y + 28, value_display, "value_chip"),
    )


def generic_horizontal_ratio_overlay(a, b, ref_a, ref_b, value_display, label_y_offset=-18):
    return primitives(
        line(a, b, "measurement_primary"),
        line(ref_a, ref_b, "reference_line"),
        dot(a),
        dot(b),
        label((a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2 + label_y_offset, value_display, "value_chip"),
    )


def brow_alignment_overlay(points, value_display):
    left = points["left_brow_mid"]
    right = points["right_brow_mid"]
    ref_left = {"x": left["x"], "y": (left["y"] + right["y"]) / 2 + 22}
    ref_right = {"x": right["x"], "y": (left["y"] + right["y"]) / 2 + 22}
    return primitives(
        line(left, right, "measurement_primary"),
        line(ref_left, ref_right, "reference_line"),
        dot(left),
        dot(right),
        label((left["x"] + right["x"]) / 2, min(left["y"], right["y"]) - 18, value_display, "value_chip"),
    )


def lip_ratio_overlay(points, value_display):
    upper_top = points["upper_lip_outer"]
    upper_bottom = points["upper_lip_inner"]
    lower_top = points["lower_lip_inner"]
    lower_bottom = points["lower_lip_outer"]

    badge_x = upper_top["x"] + 34
    badge_y = (upper_top["y"] + lower_bottom["y"]) / 2

    return primitives(
        line(upper_top, upper_bottom, "measurement_primary"),
        line(lower_top, lower_bottom, "measurement_primary"),
        dot(upper_top),
        dot(upper_bottom),
        dot(lower_top),
        dot(lower_bottom),
        label(badge_x, badge_y, value_display, "value_chip"),
    )