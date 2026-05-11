class EngineTrace:
    logs = []

    @staticmethod
    def log(stage, data):
        msg = f"\n🧠 [{stage}] {data}"
        print(msg)
        EngineTrace.logs.append(msg)
