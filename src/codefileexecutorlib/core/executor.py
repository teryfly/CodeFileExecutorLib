from typing import Generator
from codefileexecutorlib.utils.logger import Logger
from codefileexecutorlib.core.file_operations import FileOperationHandler
from codefileexecutorlib.core.parser import ContentParser
from codefileexecutorlib.core.path_handler import PathHandler
from codefileexecutorlib.utils.validators import (
    is_safe_filename, is_safe_path, is_content_length_valid
)
from codefileexecutorlib.utils.stream_handler import StreamHandler
from codefileexecutorlib.models.task_model import TaskModel
from codefileexecutorlib.models.result_model import OperationResult
from codefileexecutorlib.models.stream_data import StreamData
from codefileexecutorlib.models import StreamType
import time
import os
def is_path_length_valid(path: str, max_chars: int = 260) -> bool:
    """验证路径长度是否有效"""
    return len(path) <= max_chars
class CodeFileExecutor:
    """主执行器类，负责批量文件操作的执行"""
    def __init__(self, log_level: str = 'INFO', backup_enabled: bool = True):
        """
        初始化执行器
        Args:
            log_level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR')
            backup_enabled: 是否启用文件备份
        """
        self.logger = Logger()
        self.op_handler = FileOperationHandler(backup_enabled=backup_enabled)
        self.log_level = log_level
        self.backup_enabled = backup_enabled
    def codeFileExecutHelper(self, root_dir: str, files_content: str) -> Generator[dict, None, dict]:
        """
        执行批量文件操作的主方法
        Args:
            root_dir: 根目录路径
            files_content: 包含操作指令的内容
        Yields:
            dict: 流式执行结果，包含消息、类型、时间戳等信息
        """
        start_time = time.time()
        path_handler = PathHandler(root_dir)
        stream = StreamHandler
        parser = ContentParser
        try:
            blocks = parser.split_content(files_content)
            total_tasks = len(blocks)
            yield stream.build_stream(f"一共{total_tasks}个待执行任务", StreamType.INFO)
            self.logger.info(f"一共{total_tasks}个待执行任务")
        except Exception as e:
            yield stream.build_stream(f"内容解析失败: {str(e)}", StreamType.ERROR)
            self.logger.error(f"内容解析失败: {str(e)}")
            return
        successful_tasks = 0
        failed_tasks = 0
        invalid_tasks = 0
        content_integrity_warnings = 0
        for idx, block in enumerate(blocks):
            step_num = idx + 1
            yield stream.build_stream(f"正在解析第【{step_num}/{total_tasks}】个任务", StreamType.PROGRESS)
            self.logger.info(f"开始解析第{step_num}个任务块", step_num=step_num)
            try:
                task: TaskModel = parser.parse_task_block(block)
                if not task.is_valid:
                    invalid_tasks += 1
                    error_msg = task.error_message or "未知错误"
                    yield stream.build_stream(f"无效任务: {error_msg}", StreamType.ERROR)
                    self.logger.error(f"无效任务: {error_msg}", step_num=step_num)
                    continue
                yield stream.build_stream(task.step_line, StreamType.INFO)
                if task.code_block_count > 1:
                    msg = f"发现{task.code_block_count}个代码块，将使用最大的一个"
                    yield stream.build_stream(msg, StreamType.WARNING)
                    self.logger.warning(msg, step_num=step_num)
                content_valid, content_msg = task.validate_content_requirement()
                if not content_valid:
                    failed_tasks += 1
                    yield stream.build_stream(f"内容验证失败: {content_msg}", StreamType.ERROR)
                    self.logger.error(f"内容验证失败: {content_msg}", step_num=step_num)
                    continue
                if task.requires_content and task.content:
                    try:
                        content_verification = parser.verify_extracted_content(block, task.content)
                        if not content_verification[0]:
                            content_integrity_warnings += 1
                            msg = f"代码提取完整性警告: {content_verification[1]}"
                            yield stream.build_stream(msg, StreamType.WARNING)
                            self.logger.warning(msg, step_num=step_num)
                    except Exception as e:
                        yield stream.build_stream(f"内容验证过程出错: {str(e)}", StreamType.WARNING)
                        self.logger.warning(f"内容验证过程出错: {str(e)}", step_num=step_num)
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
                file_path = task.file_path
                is_abs = path_handler.is_absolute_path(file_path)
                if is_abs:
                    msg = "检测到绝对路径"
                    yield stream.build_stream(msg, StreamType.WARNING)
                    self.logger.warning(f"{msg}: {file_path}", step_num=step_num)
                    full_path = path_handler.normalize_path(file_path)
                else:
                    full_path = path_handler.get_full_path(file_path)
                if not path_handler.validate_path_security(full_path):
                    failed_tasks += 1
                    msg = "路径安全校验失败，跳过"
                    yield stream.build_stream(msg, StreamType.ERROR)
                    self.logger.error(f"{msg}: {full_path}", step_num=step_num)
                    continue
                filename = os.path.basename(full_path)
                if filename and not is_safe_filename(filename):
                    failed_tasks += 1
                    msg = "文件名包含非法字符，跳过"
                    yield stream.build_stream(msg, StreamType.ERROR)
                    self.logger.error(f"{msg}: {filename}", step_num=step_num)
                    continue
                try:
                    op_result = None
                    action = task.action.lower().strip()
                    operation_summary = task.get_operation_summary()
                    self.logger.info(f"执行操作: {operation_summary}", step_num=step_num)
                    if action == "create folder":
                        op_result = self.op_handler.create_folder(full_path)
                    elif action == "delete folder":
                        op_result = self.op_handler.delete_folder(full_path)
                    elif action == "create file":
                        content_length = len(task.content)
                        self.logger.info(f"创建文件，内容长度: {content_length}", step_num=step_num)
                        op_result = self.op_handler.create_file(full_path, task.content)
                    elif action == "update file":
                        content_length = len(task.content)
                        self.logger.info(f"更新文件，内容长度: {content_length}", step_num=step_num)
                        op_result = self.op_handler.update_file(full_path, task.content)
                    elif action == "delete file":
                        op_result = self.op_handler.delete_file(full_path)
                    else:
                        msg = f"不支持的操作类型: {action}"
                        failed_tasks += 1
                        yield stream.build_stream(msg, StreamType.ERROR)
                        self.logger.error(msg, step_num=step_num)
                        continue
                    if op_result and op_result.success:
                        successful_tasks += 1
                        # 统计代码行数
                        lines_count = 0
                        if task.requires_content and task.content:
                            lines_count = len(task.content.splitlines())
                        success_msg = f"任务执行成功，更新{lines_count}行代码"
                        if op_result.backup_path:
                            success_msg += f" (备份: {op_result.backup_path})"
                        yield stream.build_stream(success_msg, StreamType.SUCCESS)
                        self.logger.info(f"{success_msg}: {op_result.message}", step_num=step_num)
                    else:
                        failed_tasks += 1
                        error_msg = op_result.error if op_result else "操作返回空结果"
                        yield stream.build_stream(f"执行任务失败: {error_msg}", StreamType.ERROR)
                        self.logger.error(f"执行任务失败: {error_msg}", step_num=step_num)
                except Exception as ex:
                    failed_tasks += 1
                    error_msg = f"执行任务异常: {str(ex)}"
                    yield stream.build_stream(error_msg, StreamType.ERROR)
                    self.logger.error(error_msg, step_num=step_num)
                    continue
            except Exception as task_ex:
                failed_tasks += 1
                error_msg = f"任务处理异常: {str(task_ex)}"
                yield stream.build_stream(error_msg, StreamType.ERROR)
                self.logger.error(error_msg, step_num=step_num)
                continue
        end_time = time.time()
        execution_time = end_time - start_time
        log_file_path = getattr(self.logger, 'log_file', 'N/A')
        success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
        summary_data = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "invalid_tasks": invalid_tasks,
            "content_integrity_warnings": content_integrity_warnings,
            "success_rate": f"{success_rate:.1f}%",
            "execution_time": f"{execution_time:.2f}s",
            "log_file": log_file_path
        }
        summary_msg = f"执行完成 - 成功: {successful_tasks}, 失败: {failed_tasks}, 无效: {invalid_tasks}"
        if content_integrity_warnings > 0:
            summary_msg += f", 内容警告: {content_integrity_warnings}"
        yield stream.build_stream(summary_msg, StreamType.SUMMARY, summary_data)
        self.logger.info(
            f"执行统计: 总任务{total_tasks}, 成功{successful_tasks}, "
            f"失败{failed_tasks}, 无效{invalid_tasks}, 内容警告{content_integrity_warnings}, "
            f"成功率{success_rate:.1f}%, 耗时{execution_time:.2f}s"
        )
        return summary_data