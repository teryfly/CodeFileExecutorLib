import re
from typing import List, Tuple
from src.models.task_model import TaskModel

class ContentParser:
    @staticmethod
    def split_content(content: str) -> List[str]:
        """使用 '------' 分割内容为多个块"""
        blocks = [b.strip() for b in content.split('------') if b.strip()]
        return blocks

    @staticmethod
    def parse_task_block(block: str) -> TaskModel:
        """解析单个任务块，提取Step、Action、FilePath和代码"""
        lines = block.splitlines()
        valid, step_line, action_line, file_path_line = ContentParser.validate_task_structure(lines)
        if not valid:
            return TaskModel(
                step_line="",
                action="",
                file_path="",
                content="",
                is_valid=False,
                error_message="无效任务块",
                code_block_count=0
            )
        # 提取Action和File Path
        action = action_line.replace("Action:", "").strip()
        file_path = file_path_line.replace("File Path:", "").strip()
        # 提取代码块
        code, code_block_count = ContentParser.extract_code_blocks(block)
        return TaskModel(
            step_line=step_line,
            action=action,
            file_path=file_path,
            content=code,
            is_valid=True,
            code_block_count=code_block_count
        )

    @staticmethod
    def extract_code_blocks(content: str) -> Tuple[str, int]:
        """
        提取所有代码块内容，返回最大行数代码块和代码块数量
        """
        pattern = r"```(?:[a-zA-Z0-9]*)\n(.*?)```"
        code_blocks = re.findall(pattern, content, re.DOTALL)
        code_block_count = len(code_blocks)
        if not code_blocks:
            return ("", 0)
        max_code = max(code_blocks, key=lambda x: len(x.splitlines()))
        return (max_code.strip(), code_block_count)

    @staticmethod
    def validate_task_structure(lines: List[str]) -> Tuple[bool, str, str, str]:
        """
        验证任务结构有效性，返回 (有效, step_line, action_line, file_path_line)
        """
        step = action = path = None
        for line in lines:
            if line.strip().startswith("Step"):
                step = line.strip()
            elif line.strip().startswith("Action:"):
                action = line.strip()
            elif line.strip().startswith("File Path:"):
                path = line.strip()
        valid = bool(step and action and path)
        return (valid, step or "", action or "", path or "")