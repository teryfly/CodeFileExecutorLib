from .task_model import TaskModel
from .result_model import OperationResult
from .stream_data import StreamData
class StreamType:
    INFO = "info"
    PROGRESS = "progress"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    SUMMARY = "summary"