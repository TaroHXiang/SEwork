# Knowledge Index

本目录用于保存离线构建得到的知识检索产物：

- `knowledge.faiss`
- `metadata.json`

这些文件通常由以下推荐命令生成：

```powershell
# 推荐正式构建命令：生成持久化日志，并在存在兼容 checkpoint 时自动恢复
python scripts/build_knowledge_index.py --batch-size 256 --log-dir logs --resume

# 仅诊断：检查环境、模型加载和文档统计
python scripts/build_knowledge_index.py --diagnose-only --log-dir logs
```

说明：

- `knowledge.faiss` 是 FAISS 向量索引
- `metadata.json` 记录构建时间、embedding 模型、文档数量和知识源路径
- 构建日志会写入 `logs/knowledge-index-*.log`
- checkpoint 默认保存在 `knowledge/index/.checkpoint/`，可通过 `--resume` 恢复
- 如果你更新了 `knowledge/source/` 或 `knowledge/source/user/` 下的知识文件，建议重新生成这里的产物
