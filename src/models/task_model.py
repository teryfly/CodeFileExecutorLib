from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskModel:
    step_line: str                # Step行的完整文字
    action: str                   # 操作类型
    file_path: str                # 文件路径
    content: str                  # 代码块内容
    is_valid: bool                # 是否为有效任务
    error_message: Optional[str] = None   # 错误信息
    code_block_count: int = 0     # 代码块数量