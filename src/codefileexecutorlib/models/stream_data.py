from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class StreamData:
    message: str                  # 消息内容
    type: str                     # 消息类型: info, progress, success, error, warning, summary
    timestamp: str                # 时间戳
    data: Optional[Dict] = None   # 附加数据