from src.core.executor import CodeFileExecutor


# 日志级别: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
# 是否启用备份: True/False
executor = CodeFileExecutor(log_level='WARNING', backup_enabled=True)

# 参数1: root_dir (str) 操作根目录
root_dir= "E:\Projects\GitHubProjects\code_root_dir"

# 参数2: files_content (str) 结构化操作指令文本
files_content ="""
Step [1/15] - Create project root structure
Action: Create folder
File Path: CodeFileExecutorLib

------

Step [2/15] - Initialize main package
Action: Create file
File Path: CodeFileExecutorLib/__init__.py

```python
\"\"\"
CodeFileExecutor Library

A Python library for batch file and directory operations with streaming progress feedback.
\"\"\"

from .src.core.executor import CodeFileExecutor
from .src.models.task_model import TaskModel
from .src.models.result_model import OperationResult, StreamData
from .src.exceptions.custom_exceptions import (
    CodeFileExecutorException,
    InvalidTaskFormatException,
    PathSecurityException,
    FileOperationException
)

__version__ = "1.0.0"
__author__ = "CodeFileExecutor Team"
__email__ = "support@codefileexecutor.com"

# Main entry point
def codeFileExecutHelper(root_dir: str, files_content: str):
    \"\"\"
    Execute batch file operations with streaming progress feedback.
    
    Args:
        root_dir (str): Root directory path for operations
        files_content (str): Content containing operation instructions
    
    Returns:
        Generator: Streaming execution progress and results
    \"\"\"
    executor = CodeFileExecutor()
    return executor.codeFileExecutHelper(root_dir, files_content)

__all__ = [
    'CodeFileExecutor',
    'TaskModel',
    'OperationResult',
    'StreamData',
    'CodeFileExecutorException',
    'InvalidTaskFormatException',
    'PathSecurityException',
    'FileOperationException',
    'codeFileExecutHelper'
]
```

------

Step [3/15] - Create src package structure
Action: Create folder
File Path: CodeFileExecutorLib/src

------

Step [4/15] - Initialize src package
Action: Create file
File Path: CodeFileExecutorLib/src/__init__.py

```python
\"\"\"
Source package for CodeFileExecutor Library
\"\"\"
```

------

Step [5/15] - Create core package
Action: Create folder
File Path: CodeFileExecutorLib/src/core

------

Step [6/15] - Initialize core package
Action: Create file
File Path: CodeFileExecutorLib/src/core/__init__.py

```python
\"\"\"
Core functionality package
\"\"\"

from .executor import CodeFileExecutor
from .parser import ContentParser
from .file_operations import FileOperationHandler
from .path_handler import PathHandler

__all__ = [
    'CodeFileExecutor',
    'ContentParser', 
    'FileOperationHandler',
    'PathHandler'
]
```

------

Step [7/15] - Create models package
Action: Create folder
File Path: CodeFileExecutorLib/src/models

------

Step [8/15] - Initialize models package
Action: Create file
File Path: CodeFileExecutorLib/src/models/__init__.py

```python
\"\"\"
Data models package
\"\"\"

from .task_model import TaskModel
from .result_model import OperationResult, StreamData

__all__ = [
    'TaskModel',
    'OperationResult', 
    'StreamData'
]
```

------

Step [9/15] - Create task model
Action: Create file
File Path: CodeFileExecutorLib/src/models/task_model.py

```python
\"\"\"
Task data model definitions
\"\"\"

from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskModel:
    \"\"\"
    Data model representing a single file operation task
    \"\"\"
    step_line: str                      # Complete Step line text
    action: str                         # Operation type
    file_path: str                      # File path
    content: str                        # Code block content
    is_valid: bool                      # Whether task is valid
    error_message: Optional[str] = None # Error message if any
    code_block_count: int = 0           # Number of code blocks found
    
    def __post_init__(self):
        \"\"\"Validate task data after initialization\"\"\"
        if self.is_valid:
            if not self.step_line or not self.action or not self.file_path:
                self.is_valid = False
                self.error_message = "Missing required task components"
    
    @property
    def is_file_operation(self) -> bool:
        \"\"\"Check if this is a file operation (not folder)\"\"\"
        return self.action.lower() in ['create file', 'update file', 'delete file']
    
    @property
    def is_folder_operation(self) -> bool:
        \"\"\"Check if this is a folder operation\"\"\"
        return self.action.lower() in ['create folder', 'delete folder']
    
    @property
    def requires_content(self) -> bool:
        \"\"\"Check if this operation requires content\"\"\"
        return self.action.lower() in ['create file', 'update file']
    
    def to_dict(self) -> dict:
        \"\"\"Convert task to dictionary representation\"\"\"
        return {
            'step_line': self.step_line,
            'action': self.action,
            'file_path': self.file_path,
            'content': self.content,
            'is_valid': self.is_valid,
            'error_message': self.error_message,
            'code_block_count': self.code_block_count
        }
```

------

Step [10/15] - Create result model
Action: Create file
File Path: CodeFileExecutorLib/src/models/result_model.py

```python
\"\"\"
Result and stream data model definitions
\"\"\"

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class OperationResult:
    \"\"\"
    Data model representing the result of a file operation
    \"\"\"
    success: bool                           # Whether operation succeeded
    message: str                            # Result message
    error: Optional[str] = None             # Error information if any
    backup_path: Optional[str] = None       # Backup file path if created
    
    def to_dict(self) -> dict:
        \"\"\"Convert result to dictionary representation\"\"\"
        return {
            'success': self.success,
            'message': self.message,
            'error': self.error,
            'backup_path': self.backup_path
        }


@dataclass
class StreamData:
    \"\"\"
    Data model for streaming output data
    \"\"\"
    message: str                            # Message content
    type: str                               # Message type
    timestamp: str                          # Timestamp
    data: Optional[Dict[str, Any]] = None   # Additional data
    
    def __post_init__(self):
        \"\"\"Set timestamp if not provided\"\"\"
        if not hasattr(self, 'timestamp') or not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    @classmethod
    def create_info(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'StreamData':
        \"\"\"Create info type stream data\"\"\"
        return cls(message=message, type=StreamType.INFO, timestamp=datetime.now().isoformat(), data=data)
    
    @classmethod
    def create_progress(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'StreamData':
        \"\"\"Create progress type stream data\"\"\"
        return cls(message=message, type=StreamType.PROGRESS, timestamp=datetime.now().isoformat(), data=data)
    
    @classmethod
    def create_success(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'StreamData':
        \"\"\"Create success type stream data\"\"\"
        return cls(message=message, type=StreamType.SUCCESS, timestamp=datetime.now().isoformat(), data=data)
    
    @classmethod
    def create_error(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'StreamData':
        \"\"\"Create error type stream data\"\"\"
        return cls(message=message, type=StreamType.ERROR, timestamp=datetime.now().isoformat(), data=data)
    
    @classmethod
    def create_warning(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'StreamData':
        \"\"\"Create warning type stream data\"\"\"
        return cls(message=message, type=StreamType.WARNING, timestamp=datetime.now().isoformat(), data=data)
    
    @classmethod
    def create_summary(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'StreamData':
        \"\"\"Create summary type stream data\"\"\"
        return cls(message=message, type=StreamType.SUMMARY, timestamp=datetime.now().isoformat(), data=data)
    
    def to_dict(self) -> dict:
        \"\"\"Convert stream data to dictionary representation\"\"\"
        result = {
            'message': self.message,
            'type': self.type,
            'timestamp': self.timestamp
        }
        if self.data:
            result['data'] = self.data
        return result


class StreamType:
    \"\"\"Constants for stream data types\"\"\"
    INFO = "info"
    PROGRESS = "progress"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    SUMMARY = "summary"
```

------

Step [11/15] - Create exceptions package
Action: Create folder
File Path: CodeFileExecutorLib/src/exceptions

------

Step [12/15] - Initialize exceptions package
Action: Create file
File Path: CodeFileExecutorLib/src/exceptions/__init__.py

```python
\"\"\"
Custom exceptions package
\"\"\"

from .custom_exceptions import (
    CodeFileExecutorException,
    InvalidTaskFormatException,
    PathSecurityException,
    FileOperationException
)

__all__ = [
    'CodeFileExecutorException',
    'InvalidTaskFormatException',
    'PathSecurityException',
    'FileOperationException'
]
```

------

Step [13/15] - Create custom exceptions
Action: Create file
File Path: CodeFileExecutorLib/src/exceptions/custom_exceptions.py

```python
\"\"\"
Custom exception classes for CodeFileExecutor
\"\"\"


class CodeFileExecutorException(Exception):
    \"\"\"Base exception class for CodeFileExecutor\"\"\"
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class InvalidTaskFormatException(CodeFileExecutorException):
    \"\"\"Exception raised when task format is invalid\"\"\"
    
    def __init__(self, message: str = "Invalid task format", task_index: int = None):
        super().__init__(message, "INVALID_TASK_FORMAT")
        self.task_index = task_index
    
    def __str__(self):
        if self.task_index is not None:
            return f"[{self.error_code}] Task {self.task_index}: {self.message}"
        return super().__str__()


class PathSecurityException(CodeFileExecutorException):
    \"\"\"Exception raised when path security validation fails\"\"\"
    
    def __init__(self, message: str = "Path security violation", path: str = None):
        super().__init__(message, "PATH_SECURITY_ERROR")
        self.path = path
    
    def __str__(self):
        if self.path:
            return f"[{self.error_code}] {self.message}: {self.path}"
        return super().__str__()


class FileOperationException(CodeFileExecutorException):
    \"\"\"Exception raised when file operation fails\"\"\"
    
    def __init__(self, message: str = "File operation failed", operation: str = None, path: str = None):
        super().__init__(message, "FILE_OPERATION_ERROR")
        self.operation = operation
        self.path = path
    
    def __str__(self):
        parts = [f"[{self.error_code}]"]
        if self.operation:
            parts.append(f"{self.operation}:")
        parts.append(self.message)
        if self.path:
            parts.append(f"({self.path})")
        return " ".join(parts)
```

------

Step [14/15] - Create utils package
Action: Create folder
File Path: CodeFileExecutorLib/src/utils

------

Step [15/15] - Initialize utils package
Action: Create file
File Path: CodeFileExecutorLib/src/utils/__init__.py

```python
\"\"\"
Utility functions package
\"\"\"

from .logger import Logger
from .validators import Validators
from .stream_handler import StreamHandler

__all__ = [
    'Logger',
    'Validators',
    'StreamHandler'
]
```

"""

if __name__ == "__main__":
    for stream in executor.codeFileExecutHelper(root_dir, files_content):
        print(f"[{stream['type'].upper()}] {stream['message']}")
        if stream['type'] == 'summary':
            print("统计信息:", stream['data'])
