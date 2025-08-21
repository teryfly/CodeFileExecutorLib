import os
import shutil
import datetime
from codefileexecutorlib.models.result_model import OperationResult
class FileOperationHandler:
    def __init__(self, backup_enabled: bool = True):
        self.backup_enabled = backup_enabled
    def create_folder(self, path: str) -> OperationResult:
        try:
            os.makedirs(path, exist_ok=True)
            return OperationResult(True, "目录创建成功")
        except Exception as e:
            return OperationResult(False, "目录创建失败", error=str(e))
    def delete_folder(self, path: str) -> OperationResult:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                return OperationResult(True, "目录删除成功")
            else:
                return OperationResult(True, "目录不存在，跳过删除")
        except Exception as e:
            return OperationResult(False, "目录删除失败", error=str(e))
    def create_file(self, path: str, content: str) -> OperationResult:
        try:
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline='') as f:
                f.write(content)
            verification_result = self._verify_file_content(path, content)
            if not verification_result[0]:
                return OperationResult(False, "文件内容验证失败", error=verification_result[1])
            return OperationResult(True, "文件创建成功")
        except Exception as e:
            return OperationResult(False, "文件创建失败", error=str(e))
    def update_file(self, path: str, content: str) -> OperationResult:
        try:
            backup_path = None
            if self.backup_enabled and os.path.exists(path):
                backup_path = self.backup_file(path)
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline='') as f:
                f.write(content)
            verification_result = self._verify_file_content(path, content)
            if not verification_result[0]:
                if backup_path and os.path.exists(backup_path):
                    try:
                        shutil.copy2(backup_path, path)
                    except:
                        pass
                return OperationResult(False, "文件内容验证失败", error=verification_result[1])
            return OperationResult(True, "文件更新成功", backup_path=backup_path)
        except Exception as e:
            return OperationResult(False, "文件更新失败", error=str(e))
    def delete_file(self, path: str) -> OperationResult:
        try:
            if os.path.exists(path) and os.path.isfile(path):
                if self.backup_enabled:
                    self.backup_file(path)
                os.remove(path)
                return OperationResult(True, "文件删除成功")
            else:
                return OperationResult(True, "文件不存在，记录警告但不报错")
        except Exception as e:
            return OperationResult(False, "文件删除失败", error=str(e))
    def backup_file(self, path: str) -> str:
        try:
            backup_dir = os.path.join(os.path.dirname(path), ".backup")
            os.makedirs(backup_dir, exist_ok=True)
            base_name = os.path.basename(path)
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"{base_name}.{now}.bak")
            shutil.copy2(path, backup_path)
            return backup_path
        except Exception as e:
            return f"备份失败: {str(e)}"
    def _verify_file_content(self, file_path: str, expected_content: str) -> tuple[bool, str]:
        """验证文件内容是否与期望一致"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                actual_content = f.read()
            if actual_content != expected_content:
                if len(expected_content) != len(actual_content):
                    return False, f"内容长度不匹配: 期望{len(expected_content)}, 实际{len(actual_content)}"
                return False, "文件内容与期望内容不一致"
            return True, "内容验证通过"
        except Exception as e:
            return False, f"验证过程出错: {str(e)}"