def validate_side_inputs(pose, quality):
    issues = []

    if not pose.get("is_side_acceptable", False):
        issues.append("Pose is not ideal for side analysis. Try a cleaner profile view.")

    if quality.get("is_blurry"):
        issues.append("Image appears blurry.")
    if quality.get("is_dark"):
        issues.append("Image appears dark.")
    if quality.get("is_overbright"):
        issues.append("Image appears over-bright.")

    return issues