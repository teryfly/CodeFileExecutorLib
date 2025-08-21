import re
from typing import List, Tuple
class ContentParser:
    @staticmethod
    def split_content(content: str) -> List[str]:
        blocks = [b.strip() for b in content.split('------') if b.strip()]
        return blocks
    @staticmethod
    def parse_task_block(block: str):
        from codefileexecutorlib.models.task_model import TaskModel
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
        action = action_line.replace("Action:", "").strip()
        file_path = file_path_line.replace("File Path:", "").strip()
        raw_code_blocks, code_block_count = ContentParser.extract_code_blocks_by_string_parsing(block)
        selected_code = ""
        if raw_code_blocks:
            selected_code = raw_code_blocks[0] if len(raw_code_blocks) == 1 else max(raw_code_blocks, key=len)
        return TaskModel(
            step_line=step_line,
            action=action,
            file_path=file_path,
            content=selected_code,
            is_valid=True,
            code_block_count=code_block_count
        )
    @staticmethod
    def extract_code_blocks_by_string_parsing(content: str) -> Tuple[List[str], int]:
        """
        使用字符串解析方法提取代码块
        """
        code_blocks = []
        content_length = len(content)
        i = 0
        while i < content_length:
            start_marker = content.find('```', i)
            if start_marker == -1:
                break
            newline_after_start = content.find('\n', start_marker)
            if newline_after_start == -1:
                break
            code_start = newline_after_start + 1
            end_marker = content.find('\n```', code_start)
            if end_marker == -1:
                end_marker = content.find('```', code_start)
                if end_marker == -1:
                    break
                code_end = end_marker
            else:
                code_end = end_marker
            code_content = content[code_start:code_end]
            code_blocks.append(code_content)
            next_search_pos = end_marker + 3
            i = next_search_pos
        return code_blocks, len(code_blocks)
    @staticmethod
    def extract_raw_code_blocks(content: str) -> Tuple[List[str], int]:
        return ContentParser.extract_code_blocks_by_string_parsing(content)
    @staticmethod
    def extract_code_blocks(content: str) -> Tuple[str, int]:
        raw_blocks, count = ContentParser.extract_code_blocks_by_string_parsing(content)
        if not raw_blocks:
            return ("", 0)
        max_code = max(raw_blocks, key=len)
        return (max_code, count)
    @staticmethod
    def extract_code_blocks_fallback(content: str) -> Tuple[str, int]:
        return ContentParser.extract_code_blocks(content)
    @staticmethod
    def validate_task_structure(lines: List[str]) -> Tuple[bool, str, str, str]:
        step = action = path = None
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("Step"):
                step = line_stripped
            elif line_stripped.startswith("Action:"):
                action = line_stripped
            elif line_stripped.startswith("File Path:"):
                path = line_stripped
        valid = bool(step and action and path)
        return (valid, step or "", action or "", path or "")
    @staticmethod
    def verify_extracted_content(original_block: str, content: str) -> Tuple[bool, str]:
        if not content:
            return False, "提取的代码为空"
        critical_patterns = ['Task<', 'List<', 'Dictionary<', 'IEnumerable<']
        for pattern in critical_patterns:
            original_count = original_block.count(pattern)
            extracted_count = content.count(pattern)
            if original_count > 0 and extracted_count == 0:
                return False, f"关键泛型模式丢失: {pattern}"
            elif original_count != extracted_count:
                return False, f"泛型模式数量不匹配: {pattern} (原始:{original_count}, 提取:{extracted_count})"
        return True, "内容验证通过"