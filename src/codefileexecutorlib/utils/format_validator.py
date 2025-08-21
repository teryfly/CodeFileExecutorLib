"""
格式验证和保持工具
"""
import re
from typing import Tuple
class FormatValidator:
    """代码格式验证和保持工具"""
    @staticmethod
    def preserve_original_formatting(original: str, processed: str) -> str:
        """
        尽可能保持原始格式
        Args:
            original: 原始代码
            processed: 处理后的代码
        Returns:
            保持格式的代码
        """
        # 如果处理后的代码与原始代码在去除空白后相同，则返回原始代码
        if FormatValidator._normalize_for_comparison(original) == FormatValidator._normalize_for_comparison(processed):
            return original
        return processed
    @staticmethod
    def _normalize_for_comparison(code: str) -> str:
        """标准化代码用于比较（移除空白差异）"""
        # 移除多余空行，但保持基本结构
        lines = code.splitlines()
        normalized_lines = []
        for line in lines:
            # 保留非空行和有内容的行
            if line.strip():
                normalized_lines.append(line.rstrip())
        return '\n'.join(normalized_lines)
    @staticmethod
    def detect_format_changes(original: str, new: str) -> Tuple[bool, list]:
        """
        检测格式变化
        Returns:
            (是否有变化, 变化详情列表)
        """
        changes = []
        orig_lines = original.splitlines()
        new_lines = new.splitlines()
        # 检查行数变化
        if len(orig_lines) != len(new_lines):
            changes.append(f"行数变化: {len(orig_lines)} -> {len(new_lines)}")
        # 检查空行变化
        orig_empty_lines = sum(1 for line in orig_lines if not line.strip())
        new_empty_lines = sum(1 for line in new_lines if not line.strip())
        if orig_empty_lines != new_empty_lines:
            changes.append(f"空行数量变化: {orig_empty_lines} -> {new_empty_lines}")
        # 检查缩进变化
        orig_indents = [len(line) - len(line.lstrip()) for line in orig_lines if line.strip()]
        new_indents = [len(line) - len(line.lstrip()) for line in new_lines if line.strip()]
        if orig_indents != new_indents:
            changes.append("缩进格式发生变化")
        return len(changes) > 0, changes