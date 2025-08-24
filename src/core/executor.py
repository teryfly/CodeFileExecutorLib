from typing import Generator
from src.utils.logger import Logger
from src.core.file_operations import FileOperationHandler
from src.core.parser import ContentParser
from src.core.path_handler import PathHandler
from src.utils.validators import (
    is_safe_filename, is_safe_path, is_content_length_valid
)
from src.utils.stream_handler import StreamHandler
from src.models.task_model import TaskModel
from src.models.result_model import OperationResult
from src.models.stream_data import StreamData
from src.models import StreamType
import time
import os
def is_path_length_valid(path: str, max_chars: int = 260) -> bool:
    return len(path) <= max_chars
class CodeFileExecutor:
    def __init__(self, log_level: str = 'INFO', backup_enabled: bool = True):
        self.logger = Logger()
        self.op_handler = FileOperationHandler(backup_enabled=backup_enabled)
        self.log_level = log_level
        self.backup_enabled = backup_enabled
    def codeFileExecutHelper(self, root_dir: str, files_content: str) -> Generator[dict, None, dict]:
        start_time = time.time()
        path_handler = PathHandler(root_dir)
        stream = StreamHandler
        parser = ContentParser
        # 第一阶段：内容分割和统计
        blocks = parser.split_content(files_content)
        total_tasks = len(blocks)
        yield stream.build_stream(f"一共{total_tasks}个待执行任务", StreamType.INFO)
        self.logger.info(f"一共{total_tasks}个待执行任务")
        # 统计变量
        successful_tasks = 0
        failed_tasks = 0
        invalid_tasks = 0
        for idx, block in enumerate(blocks):
            step_num = idx + 1
            yield stream.build_stream(f"正在解析第【{step_num}/{total_tasks}】个任务", StreamType.PROGRESS)
            self.logger.info(f"开始执行第{step_num}个任务块", step_num=step_num)
            task: TaskModel = parser.parse_task_block(block)
            if not task.is_valid:
                invalid_tasks += 1
                yield stream.build_stream("无效任务", StreamType.ERROR)
                self.logger.error("无效任务", step_num=step_num)
                continue
            yield stream.build_stream(task.step_line, StreamType.INFO)
            # 多代码块警告
            if task.code_block_count > 1:
                msg = f"出现{task.code_block_count}个异常代码块数量"
                yield stream.build_stream(msg, StreamType.WARNING)
                self.logger.warning(msg, step_num=step_num)
            # 文件内容长度与路径长度校验
            if not is_content_length_valid(task.content):
                failed_tasks += 1
                msg = "文件内容超过10MB，跳过"
                yield stream.build_stream(msg, StreamType.ERROR)
                self.logger.error(msg, step_num=step_num)
                continue
            if not is_path_length_valid(task.file_path):
                failed_tasks += 1
                msg = "路径长度超过限制，跳过"
                yield stream.build_stream(msg, StreamType.ERROR)
                self.logger.error(msg, step_num=step_num)
                continue
            # 路径处理
            file_path = task.file_path
            is_abs = path_handler.is_absolute_path(file_path)
            if is_abs:
                msg = "出现异常绝对路径"
                yield stream.build_stream(msg, StreamType.WARNING)
                self.logger.warning(f"{msg}: {file_path}", step_num=step_num)
                full_path = path_handler.normalize_path(file_path)
            else:
                full_path = path_handler.get_full_path(file_path)
            # 路径安全校验
            if not path_handler.validate_path_security(full_path):
                failed_tasks += 1
                msg = "路径安全校验失败，跳过"
                yield stream.build_stream(msg, StreamType.ERROR)
                self.logger.error(msg, step_num=step_num)
                continue
            # 文件名安全校验
            filename = os.path.basename(full_path)
            if not is_safe_filename(filename):
                failed_tasks += 1
                msg = "文件名包含非法字符，跳过"
                yield stream.build_stream(msg, StreamType.ERROR)
                self.logger.error(msg, step_num=step_num)
                continue
            # 执行操作
            try:
                op_result = None
                action = task.action.lower()
                if action == "create folder":
                    op_result = self.op_handler.create_folder(full_path)
                elif action == "delete folder":
                    op_result = self.op_handler.delete_folder(full_path)
                elif action == "create file":
                    op_result = self.op_handler.create_file(full_path, task.content)
                elif action == "update file":
                    op_result = self.op_handler.update_file(full_path, task.content)
                elif action == "delete file":
                    op_result = self.op_handler.delete_file(full_path)
                else:
                    msg = "不支持的操作类型"
                    failed_tasks += 1
                    yield stream.build_stream(msg, StreamType.ERROR)
                    self.logger.error(msg, step_num=step_num)
                    continue
                if op_result.success:
                    successful_tasks += 1
                    yield stream.build_stream("任务执行成功", StreamType.SUCCESS)
                    self.logger.info("任务执行成功", step_num=step_num)
                else:
                    failed_tasks += 1
                    yield stream.build_stream(f"执行任务失败: {op_result.error}", StreamType.ERROR)
                    self.logger.error(f"执行任务失败: {op_result.error}", step_num=step_num)
            except Exception as ex:
                failed_tasks += 1
                yield stream.build_stream(f"执行任务失败: {str(ex)}", StreamType.ERROR)
                self.logger.error(f"执行任务失败: {str(ex)}", step_num=step_num)
                continue
        # 统计与汇总
        end_time = time.time()
        log_file_path = self.logger.log_file
        summary_data = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "invalid_tasks": invalid_tasks,
            "execution_time": f"{end_time - start_time:.2f}s",
            "log_file": log_file_path
        }
        yield stream.build_stream("执行完成", StreamType.SUMMARY, summary_data)
        self.logger.info(f"执行统计: 成功{successful_tasks}, 失败{failed_tasks}, 无效{invalid_tasks}")