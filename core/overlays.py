def line(p1, p2, style="measurement_primary", text=None):
    return {
        "type": "line",
        "p1": p1,
        "p2": p2,
        "style": style,
        "text": text,
    }


def dot(p, style="endpoint_dot"):
    return {
        "type": "dot",
        "x": p["x"],
        "y": p["y"],
        "style": style,
    }


def label(x, y, text, style="value_chip"):
    return {
        "type": "label",
        "x": x,
        "y": y,
        "text": text,
        "style": style,
    }


def angle(a, b, c, text, label_x=None, label_y=None, style="angle_arc"):
    return {
        "type": "angle",
        "a": a,
        "b": b,
        "c": c,
        "text": text,
        "label_x": label_x if label_x is not None else b["x"] + 28,
        "label_y": label_y if label_y is not None else b["y"] - 18,
        "style": style,
    }


def primitives(*items):
    return {"primitives": list(items)}