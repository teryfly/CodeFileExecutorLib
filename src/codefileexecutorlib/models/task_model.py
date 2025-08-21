from dataclasses import dataclass
from typing import Optional
@dataclass
class TaskModel:
    step_line: str                # Step行的完整文字
    action: str                   # 操作类型
    file_path: str                # 文件路径
    content: str                  # 代码块内容
    is_valid: bool                # 是否为有效任务
    error_message: Optional[str] = None   # 错误信息
    code_block_count: int = 0     # 代码块数量
    def __post_init__(self):
        """在初始化后进行额外的验证"""
        if self.is_valid:
            if not self.step_line or not self.action or not self.file_path:
                self.is_valid = False
                self.error_message = "缺少必要的任务组件"
    @property
    def is_file_operation(self) -> bool:
        """检查是否为文件操作（非文件夹操作）"""
        return self.action.lower() in ['create file', 'update file', 'delete file']
    @property
    def is_folder_operation(self) -> bool:
        """检查是否为文件夹操作"""
        return self.action.lower() in ['create folder', 'delete folder']
    @property
    def requires_content(self) -> bool:
        """检查此操作是否需要内容"""
        return self.action.lower() in ['create file', 'update file']
    @property
    def is_create_operation(self) -> bool:
        """检查是否为创建操作"""
        return self.action.lower() in ['create file', 'create folder']
    @property
    def is_delete_operation(self) -> bool:
        """检查是否为删除操作"""
        return self.action.lower() in ['delete file', 'delete folder']
    @property
    def is_update_operation(self) -> bool:
        """检查是否为更新操作"""
        return self.action.lower() == 'update file'
    def to_dict(self) -> dict:
        """转换为字典表示"""
        return {
            'step_line': self.step_line,
            'action': self.action,
            'file_path': self.file_path,
            'content': self.content,
            'is_valid': self.is_valid,
            'error_message': self.error_message,
            'code_block_count': self.code_block_count,
            'is_file_operation': self.is_file_operation,
            'is_folder_operation': self.is_folder_operation,
            'requires_content': self.requires_content
        }
    def validate_content_requirement(self) -> tuple[bool, str]:
        """验证内容需求是否满足"""
        if self.requires_content:
            if not self.content or self.content.strip() == "":
                return False, f"操作 '{self.action}' 需要提供内容，但内容为空"
        return True, "内容需求验证通过"
    def get_operation_summary(self) -> str:
        """获取操作摘要信息"""
        summary_parts = [
            f"操作: {self.action}",
            f"路径: {self.file_path}"
        ]
        if self.requires_content:
            content_length = len(self.content) if self.content else 0
            summary_parts.append(f"内容长度: {content_length} 字符")
        if self.code_block_count > 0:
            summary_parts.append(f"代码块数量: {self.code_block_count}")
        return " | ".join(summary_parts)