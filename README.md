# CodeFileExecutor Library

## 项目结构

```
src/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── executor.py
│   ├── parser.py
│   ├── file_operations.py
│   └── path_handler.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── validators.py
│   └── stream_handler.py
├── models/
│   ├── __init__.py
│   ├── task_model.py
│   ├── result_model.py
│   └── stream_data.py
├── exceptions/
│   ├── __init__.py
│   └── custom_exceptions.py
└── log/
    └── .gitkeep
```

## 主要入口

- `src/core/executor.py`: 主执行器，包含 `CodeFileExecutor`
- `src/core/parser.py`: 任务内容解析器
- `src/core/file_operations.py`: 文件与目录操作
- `src/core/path_handler.py`: 路径处理与安全性
- `src/utils/logger.py`: 日志系统
- `src/models/`: 数据模型定义