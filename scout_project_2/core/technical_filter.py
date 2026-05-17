def technical_filter(candidates, target_duration):
    """
    Filters candidates based on technical specifications.
    Strictly eliminates videos lower than 1080p resolution (1920x1080).
    """
    survivors = []

    for c in candidates:
        w = c.get("width", 0)
        h = c.get("height", 0)
        d = c.get("duration", 0)

        # STRICT 1080p FILTER: Minimum 1920 width or 1080 height
        if w < 1920 and h < 1080:
            continue

        # Duration check
        if d < target_duration * 0.45:
            continue

        # Aspect ratio safety check
        ratio = w / h if h else 0
        if ratio < 0.45 or ratio > 2.6:
            continue

        quality_score = (w * h) / 1000000
        duration_bonus = min(d / target_duration, 2)

        c["technical_score"] = quality_score + duration_bonus
        survivors.append(c)

    # Rank by technical merit
    survivors.sort(key=lambda x: x["technical_score"], reverse=True)
    return survivors[:50]
