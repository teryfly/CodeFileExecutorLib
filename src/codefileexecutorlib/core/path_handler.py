import os
import re

class PathHandler:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.os_type = self._detect_os_type()

    def normalize_path(self, path: str) -> str:
        if self.os_type == "windows":
            path = path.replace("/", "\\")
        else:
            path = path.replace("\\", "/")
        path = os.path.normpath(path)
        return path

    def is_absolute_path(self, path: str) -> bool:
        if self.os_type == "windows":
            return bool(re.match(r"^[a-zA-Z]:\\", path)) or path.startswith("\\")
        else:
            return path.startswith("/")

    def get_full_path(self, relative_path: str) -> str:
        rel = self.normalize_path(relative_path)
        if self.is_absolute_path(rel):
            return rel
        return os.path.normpath(os.path.join(self.root_dir, rel))

    def validate_path_security(self, path: str) -> bool:
        # 防止路径遍历攻击和根目录越界
        abs_path = os.path.abspath(path)
        root_abs = os.path.abspath(self.root_dir)
        return abs_path.startswith(root_abs)

    def _detect_os_type(self) -> str:
        win = False
        if re.match(r"^[a-zA-Z]:\\", self.root_dir) or "\\" in self.root_dir:
            win = True
        if not win and (self.root_dir.startswith("/") or "/" in self.root_dir):
            return "unix"
        return "windows" if win else "unix"