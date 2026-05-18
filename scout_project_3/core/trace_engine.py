class TraceEngine:

    @staticmethod
    def line():
        print("=" * 100)

    @staticmethod
    def section(title):
        print("\n")
        TraceEngine.line()
        print(f"🧠 {title}")
        TraceEngine.line()

    @staticmethod
    def candidate(idx, c):

        print("\n" + "-" * 80)

        print(f"🎞 CANDIDATE #{idx}")
        print(f"SOURCE            : {c.get('source')}")
        print(f"ID                : {c.get('id')}")
        print(f"RESOLUTION        : {c.get('width')}x{c.get('height')}")
        print(f"DURATION          : {c.get('duration')}s")
        print(f"TECH SCORE        : {round(c.get('technical_score',0),4)}")
        print(f"SEMANTIC SCORE    : {round(c.get('semantic_score',0),4)}")
        print(f"FAST SCORE        : {round(c.get('fast_score',0),4)}")

    @staticmethod
    def audit(result):

        print("\n🔬 MODEL FUSION")

        keys = [
            "clip_score",
            "siglip_score",
            "caption_score",
            "negative_penalty",
            "object_confidence",
            "temporal_score",
            "fusion_score",
            "confidence"
        ]

        for k in keys:
            if k in result:
                print(f"{k}: {round(result[k],4)}")

        print("\n📝 BLIP CAPTIONS")

        for c in result.get("captions", []):
            print(" •", c)

    @staticmethod
    def temporal(windows, best_start, best_end):

        print("\n⏱ TEMPORAL WINDOWS")

        for w in windows:

            star = "⭐" if w["start"] == best_start else " "

            print(
                f"{star} "
                f"{round(w['start'],2)}s → "
                f"{round(w['end'],2)}s "
                f"| SCORE={round(w['score'],4)}"
            )

        print(
            f"\n🎯 FINAL SEGMENT: "
            f"{round(best_start,2)}s → "
            f"{round(best_end,2)}s"
        )
