from sentence_transformers import util
from core.model_manager import SEMANTIC_MODEL

CACHE = {}


def emb(text):
    if text not in CACHE:
        CACHE[text] = SEMANTIC_MODEL.encode(
            text,
            convert_to_tensor=True
        )
    return CACHE[text]


def semantic_filter(scene, candidates):
    query = scene["text"]
    required = scene["scout_config"].get("must_have_required", [])
    optional = scene["scout_config"].get("must_have_optional", [])
    negative = scene.get("negative_prompts", [])

    q_full = query + " " + " ".join(required + optional)
    q_emb = emb(q_full)

    survivors = []

    for c in candidates:
        meta = (
            c.get("title", "") + " " +
            c.get("description", "")
        ).lower()

        # Mandatory Negative Filter: Reject if metadata matches any negative prompt
        if any(neg.lower() in meta for neg in negative):
            continue

        m_emb = emb(meta)
        base_score = util.cos_sim(q_emb, m_emb).item()

        # Keyword Bonus
        bonus = 0
        for r in required:
            if r.lower() in meta:
                bonus += 0.50 # Increased weight for accuracy

        for o in optional:
            if o.lower() in meta:
                bonus += 0.15

        c["semantic_score"] = base_score + bonus
        survivors.append(c)

    survivors.sort(
        key=lambda x: x["semantic_score"],
        reverse=True
    )

    return survivors[:30]
