class CodeFileExecutorException(Exception):
    """基础异常类"""
    pass

class InvalidTaskFormatException(CodeFileExecutorException):
    """无效任务格式异常"""
    pass

class PathSecurityException(CodeFileExecutorException):
    """路径安全异常"""
    pass

class FileOperationException(CodeFileExecutorException):
    """文件操作异常"""
    pass