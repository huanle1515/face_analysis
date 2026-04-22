def validate_front_inputs(pose, quality):
    issues = []

    if not pose.get("is_front_acceptable", False):
        issues.append("Pose is not ideal for front analysis. Results may be less stable.")

    if quality.get("is_blurry"):
        issues.append("Image appears blurry.")
    if quality.get("is_dark"):
        issues.append("Image appears dark.")
    if quality.get("is_overbright"):
        issues.append("Image appears over-bright.")

    return issues