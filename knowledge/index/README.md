# Knowledge Index

本目录用于保存离线构建得到的知识检索产物：

- `knowledge.faiss`
- `metadata.json`

这些文件通常由以下命令生成：

```powershell
python scripts/build_knowledge_index.py
```

说明：

- `knowledge.faiss` 是 FAISS 向量索引
- `metadata.json` 记录构建时间、embedding 模型、文档数量和知识源路径
- 如果你更新了 `knowledge/source/` 或 `knowledge/source/user/` 下的知识文件，建议重新生成这里的产物
