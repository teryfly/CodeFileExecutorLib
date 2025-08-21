"""
内容完整性验证工具
"""
import hashlib
import difflib
import re
from typing import Tuple, List
class ContentValidator:
    """内容完整性和差异验证工具"""
    @staticmethod
    def validate_content_integrity(original: str, extracted: str) -> Tuple[bool, str]:
        if len(extracted) == 0 and len(original) > 0:
            return False, "提取的内容为空"
        # 首先检查泛型类型完整性
        generic_check = ContentValidator._validate_generic_types_preservation(original, extracted)
        if not generic_check[0]:
            return False, f"泛型类型验证失败: {generic_check[1]}"
        lost_detail = ContentValidator.detect_signature_loss(original, extracted)
        if lost_detail:
            return False, lost_detail
        original_hash = hashlib.md5(original.encode('utf-8')).hexdigest()
        extracted_hash = hashlib.md5(extracted.encode('utf-8')).hexdigest()
        if original_hash == extracted_hash:
            return True, "内容完全一致"
        differences = ContentValidator.analyze_differences(original, extracted)
        return False, f"内容存在差异: {differences}"
    @staticmethod
    def analyze_differences(original: str, extracted: str) -> str:
        orig_lines = original.splitlines()
        extr_lines = extracted.splitlines()
        diff = list(difflib.unified_diff(
            orig_lines, extr_lines,
            fromfile='original', tofile='extracted',
            lineterm='', n=3
        ))
        if not diff:
            return "无明显行差异，可能是空白字符差异"
        added_lines = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        return f"添加了{added_lines}行，删除了{removed_lines}行"
    @staticmethod
    def check_code_syntax_integrity(original: str, extracted: str, file_extension: str = None) -> Tuple[bool, str]:
        # 首先检查泛型类型
        generic_check = ContentValidator._validate_generic_types_preservation(original, extracted)
        if not generic_check[0]:
            return False, f"泛型类型不完整: {generic_check[1]}"
        brackets_check = ContentValidator._check_brackets_balance(extracted)
        if not brackets_check[0]:
            return False, f"括号不匹配: {brackets_check[1]}"
        if file_extension:
            keyword_check = ContentValidator._check_language_keywords(extracted, file_extension)
            if not keyword_check[0]:
                return False, f"关键字不完整: {keyword_check[1]}"
        return True, "语法结构完整"
    @staticmethod
    def _check_brackets_balance(code: str) -> Tuple[bool, str]:
        stack = []
        bracket_pairs = {'(': ')', '[': ']', '{': '}'}  # 移除尖括号，单独处理泛型
        for i, char in enumerate(code):
            if char in bracket_pairs:
                stack.append((char, i))
            elif char in bracket_pairs.values():
                if not stack:
                    return False, f"多余的右括号 '{char}' 在位置 {i}"
                left_bracket, _ = stack.pop()
                if bracket_pairs[left_bracket] != char:
                    return False, f"括号不匹配：'{left_bracket}' 和 '{char}'"
        if stack:
            left_bracket, pos = stack[-1]
            return False, f"未闭合的左括号 '{left_bracket}' 在位置 {pos}"
        return True, "括号平衡"
    @staticmethod
    def _check_language_keywords(code: str, file_extension: str) -> Tuple[bool, str]:
        ext = file_extension.lower().lstrip('.')
        if ext in ['cs', 'csharp']:
            return ContentValidator._check_csharp_keywords(code)
        elif ext in ['js', 'ts', 'jsx', 'tsx']:
            return ContentValidator._check_js_keywords(code)
        elif ext in ['py', 'python']:
            return ContentValidator._check_python_keywords(code)
        return True, "未知语言，跳过关键字检查"
    @staticmethod
    def _check_csharp_keywords(code: str) -> Tuple[bool, str]:
        # 改进的C#泛型检查
        if 'Task<' in code:
            # 更精确的Task泛型检查
            task_generics = re.findall(r'Task<[^<>]+>', code)
            if not task_generics and 'Task<' in code:
                return False, "Task泛型类型不完整，发现 'Task<' 但没有找到完整的泛型声明"
        # 检查常见的异步方法模式
        if 'async' in code and 'Task' in code:
            # 查找 async 方法但没有完整的Task返回类型
            async_methods = re.findall(r'async\s+([^{]+)', code)
            for method in async_methods:
                if 'Task' in method and not re.search(r'Task<[^>]+>', method) and not re.search(r'\bTask\b(?!\s*<)', method):
                    return False, f"async方法可能缺少完整的Task返回类型: {method.strip()}"
        return True, "C#关键字检查通过"
    @staticmethod
    def _check_js_keywords(code: str) -> Tuple[bool, str]:
        if 'React.FC' in code and not ('=' in code and '=>' in code or 'function' in code):
            return False, "React组件定义不完整"
        return True, "JS/TS关键字检查通过"
    @staticmethod
    def _check_python_keywords(code: str) -> Tuple[bool, str]:
        if 'def ' in code:
            lines = code.split('\n')
            for line in lines:
                if line.strip().startswith('def ') and not line.strip().endswith(':'):
                    return False, f"函数定义不完整: {line.strip()}"
        return True, "Python关键字检查通过"
    @staticmethod
    def detect_signature_loss(original: str, extracted: str) -> str:
        """
        检测代码签名丢失
        改进：使用更准确的泛型检测
        """
        # 使用改进的泛型表达式提取
        original_generics = ContentValidator._extract_generic_expressions_improved(original)
        extracted_generics = ContentValidator._extract_generic_expressions_improved(extracted)
        # 检查是否有泛型表达式丢失
        for generic in original_generics:
            if generic not in extracted_generics:
                return f"泛型表达式丢失: {generic}"
        # 特别检查C#的async Task<IActionResult>模式
        if re.search(r'async\s+Task<\s*IActionResult\s*>', original) and not re.search(r'async\s+Task<\s*IActionResult\s*>', extracted):
            return "方法签名的 Task<IActionResult> 泛型返回类型丢失"
        if re.search(r'async\s+Task\b', original) and not re.search(r'async\s+Task\b', extracted):
            return "async Task 方法的 async 修饰符丢失"
        return ""
    @staticmethod
    def _extract_generic_expressions(code: str) -> List[str]:
        """
        保留原方法以兼容现有代码
        """
        return ContentValidator._extract_generic_expressions_improved(code)
    @staticmethod
    def _extract_generic_expressions_improved(code: str) -> List[str]:
        """
        改进的泛型表达式提取方法
        """
        generic_expressions = []
        # 改进的泛型模式，更精确地匹配
        patterns = [
            r'\bTask<[^<>{}]+>',              # Task<IActionResult>, Task<string> 等
            r'\bList<[^<>{}]+>',              # List<string>, List<User> 等
            r'\bIEnumerable<[^<>{}]+>',       # IEnumerable<string> 等
            r'\bDictionary<[^<>{}]+,\s*[^<>{}]+>', # Dictionary<string, object> 等
            r'\bAction<[^<>{}]+>',            # Action<string> 等
            r'\bFunc<[^<>{}]+>',              # Func<string, bool> 等
            r'\b[A-Z]\w*<[^<>{}]+>',          # 其他泛型类型
        ]
        for pattern in patterns:
            matches = re.findall(pattern, code)
            generic_expressions.extend(matches)
        # 去重
        return list(set(generic_expressions))
    @staticmethod
    def _validate_generic_types_preservation(original: str, extracted: str) -> Tuple[bool, str]:
        """
        验证泛型类型是否在提取过程中得到保留
        """
        original_generics = ContentValidator._extract_generic_expressions_improved(original)
        extracted_generics = ContentValidator._extract_generic_expressions_improved(extracted)
        if not original_generics:
            return True, "无泛型类型需要验证"
        missing_generics = []
        for generic in original_generics:
            if generic not in extracted_generics:
                missing_generics.append(generic)
        if missing_generics:
            return False, f"以下泛型类型在提取过程中丢失: {', '.join(missing_generics)}"
        # 检查是否有泛型语法错误
        for generic in extracted_generics:
            if generic.count('<') != generic.count('>'):
                return False, f"泛型类型语法错误: {generic}"
        return True, "泛型类型保留完整"