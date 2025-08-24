import datetime

class StreamHandler:
    def build_stream(self, message: str, type_: str, data: dict = None):
        now = datetime.datetime.now().isoformat(timespec="seconds")
        return {
            "message": message,
            "type": type_,
            "timestamp": now,
            "data": data
        }