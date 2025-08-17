# CodeFileExecutorLib API 使用文档

## 1. 安装与集成

将 `src/` 目录和 `CodeFileExecutorLib.py` 放入你的工程目录（如可打包为 pip 包，按标准放置即可）。

示例项目结构：

```
your_project/
├── CodeFileExecutorLib.py
├── src/
│   └── ...（全部包内容）
├── your_code.py
```

## 2. API 说明

### 2.1 导入主类

```python
from CodeFileExecutorLib import CodeFileExecutor
```

### 2.2 创建执行器实例

```python
# 日志级别: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
# 是否启用备份: True/False
executor = CodeFileExecutor(log_level='INFO', backup_enabled=True)
```

### 2.3 执行批量文件操作

```python
# 参数1: root_dir (str) 操作根目录
# 参数2: files_content (str) 结构化操作指令文本
results = []
for result in executor.codeFileExecutHelper(root_dir, files_content):
    print(f"[{result['type'].upper()}] {result['message']}")
    results.append(result)

# 汇总统计信息
summary = results[-1] if results and results[-1]['type'] == 'summary' else None
print("最终统计：", summary)
```

### 2.4 流式数据格式

每个流式输出字典包含：
- message (str): 消息内容
- type (str): 信息类型（info, progress, success, warning, error, summary）
- timestamp (str): 时间戳
- data (dict): 附加数据（summary 类型才有）

### 2.5 日志文件

- 日志默认写入 `src/log/execution_YYYYMMDD_HHMMSS.log`
- 格式为 `[时间戳] [级别] [Step N] 消息内容`

---

## 3. files_content 指令格式

每个任务块必须包含：
1. `Step [X/Y] - ...`
2. `Action: ...`
3. `File Path: ...`
4. 可选代码块（用于文件操作）

多个任务块用六个横线分割（`------`）。

### 示例

```
Step [1/2] - Create data folder
Action: Create folder
File Path: data
------------------- End -------------------