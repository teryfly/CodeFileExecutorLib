import datetime

class StreamHandler:
    @staticmethod
    def build_stream(message: str, type_: str, data: dict = None):
        now = datetime.datetime.now().isoformat(timespec="seconds")
        return {
            "message": message,
            "type": type_,
            "timestamp": now,
            "data": data
        }