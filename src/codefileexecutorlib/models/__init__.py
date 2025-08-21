# 为了避免在包初始化时触发循环导入，这里不在顶层执行深层导入
# 使用显式导入路径：from codefileexecutorlib.models.task_model import TaskModel 等
from .result_model import OperationResult
from .stream_data import StreamData
class StreamType:
    INFO = "info"
    PROGRESS = "progress"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    SUMMARY = "summary"
__all__ = [
    'OperationResult',
    'StreamData',
    'StreamType',
    # 不在此处导出 TaskModel，避免第三方在导入 models 时触发 task_model 的初始化
]