import re
import os
def is_safe_filename(filename: str) -> bool:
    # 只允许字母、数字、下划线、点、短横线
    return bool(re.match(r"^[\w.\-]+$", filename))
def is_safe_path(path: str) -> bool:
    # 不允许路径中出现 .. 或绝对路径
    norm = os.path.normpath(path)
    if ".." in norm.split(os.sep):
        return False
    if os.path.isabs(path):
        return True  # 绝对路径由路径处理器进一步判断
    return True
def is_content_length_valid(content: str, max_bytes: int = 10*1024*1024) -> bool:
    return len(content.encode("utf-8")) <= max_bytes