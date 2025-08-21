from dataclasses import dataclass
from typing import Optional

@dataclass
class OperationResult:
    success: bool                       # 操作是否成功
    message: str                        # 结果消息
    error: Optional[str] = None         # 错误信息
    backup_path: Optional[str] = None   # 备份文件路径（如有）