"""
预处理工具：在解析之前对整体文本进行规整
"""
import re
from typing import Optional


class Preprocessor:
    """
    对 LLM assistant 回复文本做统一规整处理
    1. 删除开头所有“思索、推理、反思”类标签/片段
    2. 删除结尾 [to be continued]/[to be continue]
    """

    _think_start_pattern = re.compile(
        "|".join(
            [
                r"^\s*<think>[\s\S]*?</think>\s*",
                r"^\s*\*Thinking.*?\*\s*",
                r"^\s*(?:Thinking\.\.\.\s*\(\d+s elapsed\)\s*)+",
                r"^\s*[-*\u2022]?\s*(?:Thinking|Reflection|Reasoning|思考|推理|反思)[:：].*?\n+",
                r"^\s*(?:让我们思考一下|以下是我的推理|推理如下|思考如下)[：:]?\s*\n+",
                r"^\s*>[^\n]*\n+",
            ]
        ),
        re.IGNORECASE,
    )

    _to_be_continued_pattern = re.compile(r"\s*\[to be continue(?:d)?\]\s*$", re.IGNORECASE)

    @staticmethod
    def trim_assistant_reply(content: Optional[str]) -> str:
        if not content:
            return "" if content is None else content

        result = content

        while True:
            prev = result
            result = Preprocessor._think_start_pattern.sub("", result)
            if result == prev:
                break

        result = Preprocessor._to_be_continued_pattern.sub("", result)

        return result.strip()