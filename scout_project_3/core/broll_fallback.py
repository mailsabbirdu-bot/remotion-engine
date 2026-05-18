def choose_broll(scene):

    fallback = scene.get("fallback_broll")

    if not fallback:
        return None

    return fallback
