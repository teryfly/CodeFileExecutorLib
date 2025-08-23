# 📘 CodeFileExecutorLib API 文档

## 安装

在第三方项目中使用之前，先通过 `pip` 安装：

### 方式一：本地源码安装
```bash
# 在 CodeFileExecutorLib 项目根目录执行
pip install .
```

### 方式二：打包并安装
```bash
python setup.py sdist bdist_wheel
pip install dist/CodeFileExecutorLib-1.0.0-py3-none-any.whl
```

### 方式三：从 Git 仓库安装
```bash
pip install git+https://github.com/teryfly/CodeFileExecutorLib.git
```

---

## 使用示例

### 引入库
```python
from codefileexecutorlib  import CodeFileExecutor
```

### 创建执行器实例
```python
# 日志级别: DEBUG / INFO / WARNING / ERROR
# 是否启用备份: True/False
executor = CodeFileExecutor(log_level="ERROR", backup_enabled=False)
```

### 执行操作任务
```python
root_dir = "/path/to/project"

files_content = """
Step [1/2] - Create config directory
Action: Create folder
File Path: config

------
Step [2/2] - Create config file
Action: Create file
File Path: config/app.json
```json
{
  "name": "MyApp",
  "version": "1.0.0"
}
```
"""

for stream in executor.codeFileExecutHelper(root_dir, files_content):
    print(f"[{stream['type'].upper()}] {stream['message']}")
    if stream['type'] == 'summary':
        print("统计信息:", stream['data'])
```

---

## API 说明

### `class CodeFileExecutor`

#### 构造函数
```python
CodeFileExecutor(log_level: str = "INFO", backup_enabled: bool = True)
```
- **参数**
  - `log_level` (str): 日志级别，可选 `DEBUG` / `INFO` / `WARNING` / `ERROR`
  - `backup_enabled` (bool): 是否启用文件备份功能

---

#### 方法：`codeFileExecutHelper`
```python
def codeFileExecutHelper(root_dir: str, files_content: str) -> Generator[dict, None, dict]
```
- **参数**
  - `root_dir`: 根目录路径
  - `files_content`: 任务定义内容（符合规范的结构化文本）
- **返回**
  - 一个 **生成器**，逐步返回任务执行的流式结果

---

## 流式返回数据结构

每条结果为一个 `dict`：

```json
{
  "message": "任务执行成功",
  "type": "success",
  "timestamp": "2025-08-18T14:30:25",
  "data": { }
}
```

- **type 可选值**
  - `info`: 一般信息
  - `progress`: 进度信息
  - `success`: 成功信息
  - `error`: 错误信息
  - `warning`: 警告信息
  - `summary`: 汇总信息

- **summary 样例**
```json
{
  "message": "执行完成",
  "type": "summary",
  "timestamp": "2025-08-18T14:30:30",
  "data": {
    "total_tasks": 5,
    "successful_tasks": 4,
    "failed_tasks": 1,
    "invalid_tasks": 0,
    "execution_time": "2.34s",
    "log_file": "log/execution_20250818_143025.log"
  }
}
```

---

## 注意事项
- 引入库时要使用全小写 （ from codefileexecutorlib  import CodeFileExecutor ）
- 所有文件操作都受 **路径安全验证** 限制，防止目录遍历攻击
- 文件大小限制：单文件最大 10MB
- 路径长度限制：260 字符（兼容 Windows）
- 建议在 Linux / macOS 下使用 `/` 路径分隔符，在 Windows 下使用 `\`

---
