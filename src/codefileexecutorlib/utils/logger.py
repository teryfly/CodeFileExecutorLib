import os
import datetime

class Logger:
    def __init__(self, log_dir: str = 'src/log'):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = self._create_log_file()

    def info(self, message: str, step_num: int = None):
        self._write_log("INFO", message, step_num)

    def warning(self, message: str, step_num: int = None):
        self._write_log("WARNING", message, step_num)

    def error(self, message: str, step_num: int = None):
        self._write_log("ERROR", message, step_num)

    def _write_log(self, level: str, message: str, step_num: int = None):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{now}] [{level}]"
        if step_num is not None:
            prefix += f" [Step {step_num}]"
        log_content = f"{prefix} {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_content)

    def _create_log_file(self) -> str:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"execution_{now}.log"
        return os.path.join(self.log_dir, filename)