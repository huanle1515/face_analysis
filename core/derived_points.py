from core.geometry import midpoint, mean_point, point


def lerp_point(a, b, t):
    return point(
        a["x"] + (b["x"] - a["x"]) * t,
        a["y"] + (b["y"] - a["y"]) * t,
    )


def build_front_derived_points(pts):
    # eye centers
    left_eye_center = mean_point([
        pts["left_eye_outer"],
        pts["left_eye_inner"],
        pts["left_upper_lid"],
        pts["left_lower_lid"],
    ])
    right_eye_center = mean_point([
        pts["right_eye_outer"],
        pts["right_eye_inner"],
        pts["right_upper_lid"],
        pts["right_lower_lid"],
    ])

    # mouth / lips
    mouth_center = midpoint(pts["mouth_left"], pts["mouth_right"])
    upper_lip_center = mean_point([pts["upper_lip_outer"], pts["upper_lip_inner"]])
    lower_lip_center = mean_point([pts["lower_lip_inner"], pts["lower_lip_outer"]])

    # face width anchors
    left_face_stable = mean_point([pts["left_zygion"], pts["left_cheek"]])
    right_face_stable = mean_point([pts["right_zygion"], pts["right_cheek"]])

    # jaw anchors
    left_jaw_stable = pts["left_jaw"]
    right_jaw_stable = pts["right_jaw"]

    # chin
    chin_stable = mean_point([pts["chin"], pts["pogonion"]])

    # top anchor:
    # keep using upper-face proxy, but not raw hairline.
    top_stable = mean_point([pts["top"], pts["glabella"]])

    # -------- better anatomical subnasale proxy --------
    # raw MediaPipe "subnasale" can be noisy. Build a more stable point:
    # 1) midpoint of alar base (nose_left / nose_right)
    alar_mid = midpoint(pts["nose_left"], pts["nose_right"])

    # 2) point from nose tip toward upper lip center
    nose_to_lip_mid = midpoint(pts["nose_tip"], upper_lip_center)

    # 3) combine with columella / philtrum base
    subnasale_stable = mean_point([
        pts["subnasale"],
        pts["columella"],
        pts["philtrum_base"],
        alar_mid,
        nose_to_lip_mid,
    ])

    # -------- better nose-width anchors --------
    # raw nose_left/right can be too wide. Pull slightly inward toward nostril center line.
    left_alar = lerp_point(alar_mid, pts["nose_left"], 0.72)
    right_alar = lerp_point(alar_mid, pts["nose_right"], 0.72)

    # centerline
    face_center_x = (left_face_stable["x"] + right_face_stable["x"]) / 2.0

    return {
        "left_eye_center": left_eye_center,
        "right_eye_center": right_eye_center,
        "mouth_center": mouth_center,
        "upper_lip_center": upper_lip_center,
        "lower_lip_center": lower_lip_center,
        "chin_stable": chin_stable,
        "subnasale_stable": subnasale_stable,
        "left_face_stable": left_face_stable,
        "right_face_stable": right_face_stable,
        "left_jaw_stable": left_jaw_stable,
        "right_jaw_stable": right_jaw_stable,
        "left_alar": left_alar,
        "right_alar": right_alar,
        "alar_mid": alar_mid,
        "top_stable": top_stable,
        "face_center_x": face_center_x,
        "face_midline_top": point(face_center_x, top_stable["y"]),
        "face_midline_bottom": point(face_center_x, chin_stable["y"]),
    }


def build_side_derived_points(pts):
    lip_mid = midpoint(pts["upper_lip_front"], pts["lower_lip_front"])
    subnasale_stable = mean_point([pts["subnasale"], pts["columella"]])
    chin_stable = mean_point([pts["pogonion"], pts["chin"]])
    browridge_stable = mean_point([pts["browridge_profile"], pts["glabella"]])

    return {
        "lip_mid": lip_mid,
        "subnasale_stable": subnasale_stable,
        "chin_stable": chin_stable,
        "browridge_stable": browridge_stable,
    }