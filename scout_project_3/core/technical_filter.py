def technical_filter(candidates, target_duration):
    """
    Filters candidates based on technical specifications.
    Strictly eliminates videos lower than 2K resolution (2560x1440).
    """
    survivors = []

    for c in candidates:
        w = c.get("width", 0)
        h = c.get("height", 0)
        d = c.get("duration", 0)

        # STRICT 2K FILTER: Minimum 2560 width or 1440 height (to allow for portrait/square 2K)
        if w < 2560 and h < 1440:
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
