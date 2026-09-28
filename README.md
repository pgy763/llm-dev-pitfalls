# LLM 应用开发踩坑手册

> 你在深夜遇到的那些报错，这里可能都记着。

用 LangChain（Python）/ LangChain4j / Spring AI 写 AI 应用时踩过的坑，**按报错关键词索引**。
不用从头读——把报错信息复制进来，`Ctrl+F` 搜一下就行。

---

## 这个仓库和别处有什么不同

大部分教程教你「怎么写对」，这里只记「怎么写错、以及为什么错」。

- **按报错索引，不按学习顺序** —— 你手上只有一条报错，没有章节号
- **每条坑四段固定结构** —— 报错原文 / 为什么 / 怎么改 / 怎么预防
- **每条都标了环境版本** —— 大部分坑的根因是版本差异，不标版本等于没写
- **只收真实踩过的** —— 每条都来自真实调试过程，不是从官方文档里抄的

## 怎么用

1. 把报错信息复制进来，`Ctrl+F` 搜索**最独特的那个词**（比如 `PydanticUserError`、`seacher`），不要搜 `Error` 这种到处都有的词
2. 找到对应文件，重点看「为什么」和「怎么改」两节
3. 搜不到？开一个 [Issue](../../issues/new?template=new-pitfall.md) 把报错原文贴上来，我来补

## 索引

### 密钥与鉴权

| 报错关键词 | 一句话原因 | 文件 |
| --- | --- | --- |
| `OpenAIError: The api_key client option must be set` | `.env` 不存在、没加载，或工作目录不对 | [看](docs/auth/openai-error-api-key-not-set.md) |
| `401 Authentication Fails` | key、URL、客户端、模型名四件套不是同一家 | [看](docs/auth/401-authentication-fails-key-mismatch.md) |
| `503 分组 default 下无可用渠道` | 中转站的 key 所在分组没有该模型 | [看](docs/auth/upstream-503-no-channel.md) |

### 接口地址与模型名

| 报错关键词 | 一句话原因 | 文件 |
| --- | --- | --- |
| 请求 `404`，URL 看起来完全正确 | `base_url` 写到了 `/chat/completions`，SDK 会自己拼 | [看](docs/endpoint/base-url-404.md) |
| `model_not_found` / `模型不存在` | 模型名少了版本后缀，或别名已下线 | [看](docs/endpoint/model-not-found.md) |

### 环境与编码

| 报错关键词 | 一句话原因 | 文件 |
| --- | --- | --- |
| `UnicodeDecodeError: 'gbk' codec can't decode` | Windows 下读 `.env`，中文注释 + GBK 编码冲突 | [看](docs/env/gbk-codec-unicodedecodeerror.md) |
| `invalid literal for int() with base 10: '(3306,)'` | 赋值行多了个尾逗号，变量变成了元组 | [看](docs/env/trailing-comma-tuple.md) |
| `unexpected keyword argument 'charset '` | URL 参数等号两边有空格 | [看](docs/env/url-param-space.md) |

### Python 与类型

| 报错关键词 | 一句话原因 | 文件 |
| --- | --- | --- |
| `PydanticUserError: Field 'description' defined on a base class was overridden` | pydantic v2 要求覆盖基类字段必须带类型注解 | [看](docs/python/pydantic-v2-field-overridden.md) |
| `string indices must be integers` | 把返回的 `list[str]` 当成 `dict` 用了 | [看](docs/python/string-indices-must-be-integers.md) |
| `no attribute 'web_seacher'` | 拼写错误，报错信息里的 `Did you mean` 就是答案 | [看](docs/python/attribute-typo-seacher.md) |
| `No module named 'my_llm'` | 裸导入在 langgraph 加载方式下失效，要走包路径 | [看](docs/python/no-module-named.md) |

### Agent 与工具设计

| 现象 | 一句话原因 | 文件 |
| --- | --- | --- |
| SQL 检查工具判定「通过」，实际执行却报语法错 | 纯关键字检查不验证语法，需要用 `EXPLAIN` 干跑 | [看](docs/agent/sql-check-misses-syntax-error.md) |

## 环境对照

本仓库的坑主要在下面这套环境下复现：

| 组件 | 版本 |
| --- | --- |
| Python | 3.13 |
| LangChain | 1.x |
| langgraph | 最新 |
| pydantic | v2 |
| 模型提供方 | 阿里云百炼（兼容模式）/ 智谱 / DeepSeek / 各类中转站 |
| 操作系统 | Windows 11 |

**注意**：如果你的环境不一样，坑的表现可能不同——但根因往往一致。每条坑文件末尾都标了原始环境。

## 路线图

- [x] LangChain（Python）实战坑
- [ ] LangChain4j（Java）实战坑
- [ ] Spring AI 实战坑
- [ ] RAG 专项：召回质量、切分参数、评估
- [ ] Agent 专项：工具调用失败、循环终止、上下文超限

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。最简单的参与方式：开一个 Issue，把你刚踩的坑贴上来（报错原文 + 你怎么解决的就行，格式我来整理）。

**这个仓库的价值等于里面坑的数量。** 你多贴一条，下一个搜到它的人就少熬一次夜。

## License

MIT
