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

    required = scene["scout_config"].get(
        "must_have_required",
        []
    )

    optional = scene["scout_config"].get(
        "must_have_optional",
        []
    )

    q = query + " " + " ".join(required + optional)

    q_emb = emb(q)

    for c in candidates:

        meta = (
            c.get("title", "") + " " +
            c.get("description", "")
        )

        m_emb = emb(meta)

        score = util.cos_sim(q_emb, m_emb).item()

        bonus = 0

        for r in required:
            if r.lower() in meta.lower():
                bonus += 0.25

        for o in optional:
            if o.lower() in meta.lower():
                bonus += 0.08

        penalty = 0

        for neg in scene.get("negative_prompts", []):
            if neg.lower() in meta.lower():
                penalty += 0.3

        c["semantic_score"] = score + bonus - penalty

    candidates.sort(
        key=lambda x: x["semantic_score"],
        reverse=True
    )

    return candidates[:20]
