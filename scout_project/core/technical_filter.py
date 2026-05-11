def technical_filter(candidates, target_duration):

    survivors = []

    for c in candidates:

        w = c.get("width", 0)
        h = c.get("height", 0)
        d = c.get("duration", 0)

        if w < 640 or h < 360:
            continue

        if d < target_duration * 0.45:
            continue

        ratio = w / h if h else 0

        if ratio < 0.45 or ratio > 2.6:
            continue

        quality = (w * h) / 1000000

        duration_bonus = min(d / target_duration, 2)

        c["technical_score"] = quality + duration_bonus

        survivors.append(c)

    survivors.sort(
        key=lambda x: x["technical_score"],
        reverse=True
    )

    return survivors[:40]
