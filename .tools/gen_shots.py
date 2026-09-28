"""为每条坑生成一张终端风格的报错截图。

用法：
    python gen_shots.py

输出：../images/<name>.png

改图只需改 SHOTS 里的文本，然后重跑。
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W = 1000
BAR_H = 34
PAD_T = 16
LINE_H = 25
PAD_B = 16

BG = (30, 30, 34)
BAR = (50, 50, 58)
DOT = ((255, 95, 87), (254, 188, 46), (40, 200, 64))

TXT = (212, 212, 214)
DIM = (138, 138, 144)
RED = (244, 135, 113)
GRN = (137, 209, 133)
YEL = (220, 220, 170)
BLU = (110, 170, 220)

COLORS = {"w": TXT, "d": DIM, "r": RED, "g": GRN, "y": YEL, "b": BLU}

EN_PATH = "C:/Windows/Fonts/consola.ttf"
CN_PATH = "C:/Windows/Fonts/msyh.ttc"

_cache = {}


def font(size, cn=False):
    key = (size, cn)
    if key not in _cache:
        path = CN_PATH if cn else EN_PATH
        try:
            _cache[key] = ImageFont.truetype(path, size, index=0)
        except Exception:
            try:
                _cache[key] = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", size)
            except Exception:
                _cache[key] = ImageFont.load_default()
    return _cache[key]


def is_cn(ch):
    o = ord(ch)
    return (0x3000 <= o <= 0x303F) or (0x4E00 <= o <= 0x9FFF) or (0xFF00 <= o <= 0xFFEF) or (0x2000 <= o <= 0x206F)


def draw_line(d, x, y, text, fe, fc, color):
    """逐段渲染，中文走中文字体、英文走等宽字体，避免出现豆腐块。"""
    if not text:
        return
    buf = ""
    cur = None
    for ch in text:
        c = is_cn(ch)
        if cur is None:
            buf, cur = ch, c
        elif c == cur:
            buf += ch
        else:
            f = fc if cur else fe
            d.text((x, y), buf, font=f, fill=color)
            x += d.textlength(buf, font=f)
            buf, cur = ch, c
    f = fc if cur else fe
    d.text((x, y), buf, font=f, fill=color)


def render(name, title, body, outdir):
    rows = []
    for raw in body.strip("\n").split("\n"):
        if raw == "":
            rows.append(("", TXT))
            continue
        tag, sep, text = raw.partition("|")
        rows.append((text, COLORS.get(tag, TXT)))

    h = BAR_H + PAD_T + len(rows) * LINE_H + PAD_B
    img = Image.new("RGB", (W * SCALE, h * SCALE), BG)
    d = ImageDraw.Draw(img)
    S = SCALE

    d.rectangle([0, 0, W * S, BAR_H * S], fill=BAR)
    for i, c in enumerate(DOT):
        cx = (18 + i * 18) * S
        cy = (BAR_H / 2) * S
        r = 5 * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    draw_line(d, 78 * S, 10 * S, title, font(13 * S), font(14 * S, cn=True), DIM)

    fe, fc = font(15 * S), font(16 * S, cn=True)
    y = (BAR_H + PAD_T) * S
    for text, color in rows:
        draw_line(d, 20 * S, y, text, fe, fc, color)
        y += LINE_H * S

    path = os.path.join(outdir, name + ".png")
    img.save(path, "PNG", optimize=True)
    return path


SHOTS = [
    ("api-key-not-set", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/text_to_sql_agent.py", line 12, in <module>
d|    llm = ChatOpenAI(model="qwen-plus",
d|                      api_key=os.getenv("DASHSCOPE_API_KEY"))
d|  File "langchain_openai/chat_models/base.py", line 128, in __init__
d|    self._client = OpenAI(api_key=api_key, base_url=base_url)
r|openai.OpenAIError: The api_key client option must be set either by
r|passing api_key to the client or by setting the OPENAI_API_KEY
r|environment variable
"""),

    ("401-key-mismatch", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/text_to_sql_agent.py", line 28, in <module>
d|    resp = llm.invoke("你好")
d|  File "openai/_base_client.py", line 1074, in _request
r|openai.AuthenticationError: Error code: 401 - {'error':
r|{'message': 'Authentication Fails, Your api key is invalid',
r|'type': 'authentication_error', 'param': None, 'code': None}}
"""),

    ("503-no-channel", "$ curl -X POST $BASE_URL/chat/completions \\", """
r|openai.APIStatusError: Error code: 503 - {'error':
r|{'message': '分组 default 下无可用渠道', 'type': 'api_error'}}
"""),

    ("base-url-404", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/text_to_sql_agent.py", line 28, in <module>
d|    resp = llm.invoke("你好")
d|  File "openai/_base_client.py", line 1074, in _request
r|openai.NotFoundError: Error code: 404 - {'error':
r|{'message': 'Not Found', 'type': 'invalid_request_error'}}
d|
d|（base_url 写成了 https://api.deepseek.com/v1/chat/completions
d|  SDK 会自己再拼一次 /chat/completions，于是路径重复）
"""),

    ("model-not-found", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/text_to_sql_agent.py", line 28, in <module>
d|    resp = llm.invoke("你好")
d|  File "openai/_base_client.py", line 1074, in _request
r|openai.NotFoundError: Error code: 404 - {'error':
r|{'message': 'model_not_found', 'type': 'invalid_request_error',
r|'code': 'invalid_parameter_error'}}
"""),

    ("gbk-encoding", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/text_to_sql_agent.py", line 8, in <module>
d|    load_dotenv(verbose=True)
d|  File "dotenv/main.py", line 122, in load_dotenv
d|    return DotEnv(f, verbose=verbose, encoding=encoding)
d|  File "encodings/gbk.py", line 63, in decode
r|UnicodeDecodeError: 'gbk' codec can't decode byte 0x80 in position 12:
r|illegal multibyte sequence
"""),

    ("trailing-comma-tuple", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/text_to_sql_agent.py", line 34, in <module>
d|    manager = MySQLDatabaseManager(connection(**cfg))
d|  File "src/agent/utils/db_utils.py", line 24, in __init__
d|    self.engine = create_engine(connection, pool_size=5)
r|ValueError: invalid literal for int() with base 10: '(3306,)'
d|
d|（port = 3306, 后面那个逗号让它变成了元组）
"""),

    ("url-param-space", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/utils/db_utils.py", line 24, in __init__
d|    self.engine = create_engine(connection)
r|TypeError: create_engine() got an unexpected keyword argument 'charset '
d|
d|（连接串写成了 ?charset = utf8mb4，等号两边有空格）
"""),

    ("pydantic-v2-annotation", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/tool/sql_tools.py", line 18, in <module>
d|    class QuerySQLTool(BaseTool):
d|  File "pydantic/_internal/_model_construction.py", line 226, in __new__
r|pydantic.errors.PydanticUserError: Field 'description' defined on a
r|base class was overridden by a non-annotated attribute.
r|Adding a type annotation is required.
"""),

    ("list-as-dict", "$ python src/agent/text_to_sql_agent.py", """
d|Traceback (most recent call last):
d|  File "src/agent/tool/sql_tools.py", line 31, in _run
d|    for t in table_names:
d|        name = t['name']
r|TypeError: string indices must be integers, not 'str'
d|
d|（get_table_names() 返回的是 list[str]，不是 list[dict]）
"""),

    ("attribute-typo", "$ python src/agent/tool/tool_demo1.py", """
d|Traceback (most recent call last):
d|  File "src/agent/tool/tool_demo1.py", line 22, in <module>
d|    result = client.web_seacher(query="LangChain 是什么")
r|AttributeError: 'ZhipuAI' object has no attribute 'web_seacher'.
r|Did you mean: 'web_search'?
"""),

    ("module-not-found", "$ langgraph dev", """
d|Traceback (most recent call last):
d|  File "src/agent/text_to_sql_agent.py", line 6, in <module>
d|    from my_llm import llm
r|ModuleNotFoundError: No module named 'my_llm'
d|
d|（直接 python 跑能通，langgraph dev 走包路径加载就不行）
"""),

    ("sql-check-miss", "$ python src/agent/text_to_sql_agent.py", """
g|$ sql_db_check("select departments")
g|检查通过：这是一个安全的只读查询。
d|
r|$ sql_db_query("select departments")
r|查询失败：(1064, "You have an error in your SQL syntax;
r|check the manual that corresponds to your MySQL server version")
d|
d|（关键字检查只看了开头是不是 SELECT，没验语法）
"""),

    ("context-too-long", "$ python src/agent/summarize.py", """
d|Traceback (most recent call last):
d|  File "src/agent/summarize.py", line 41, in <module>
d|    resp = llm.invoke(messages)
d|  File "openai/_base_client.py", line 1074, in _request
r|openai.BadRequestError: Error code: 400 - {'error':
r|{'message': "This model's maximum context length is 16385 tokens.
r|However, your messages resulted in 24187 tokens.", 
r|'code': 'context_length_exceeded'}}
"""),

    ("rate-limit-429", "$ python src/agent/batch_generate.py", """
d|  完成 12/500 ...
d|  完成 13/500 ...
d|Traceback (most recent call last):
d|  File "src/agent/batch_generate.py", line 57, in <module>
d|    resp = llm.invoke(prompt)
r|openai.RateLimitError: Error code: 429 - {'error':
r|{'message': 'Rate limit reached for requests. Please retry later.',
r|'type': 'rate_limit_error'}}
d|
d|（500 条循环里没有限速，也没有重试）
"""),

    ("output-parser-error", "$ python src/agent/extract.py", """
d|Traceback (most recent call last):
d|  File "src/agent/extract.py", line 33, in <module>
d|    result = chain.invoke({"text": resume})
d|  File "langchain_core/output_parsers/json.py", line 74, in parse_result
r|langchain_core.exceptions.OutputParserException:
r|Could not parse LLM output: `好的，以下是 JSON 格式的结果：
r|```json
r|{"name": "张三", "age": 25}
r|``` 希望对你有所帮助！`
"""),

    ("agent-infinite-loop", "$ python src/agent/text_to_sql_agent.py", """
d|Thought: 我需要先看看有哪些表
d|Action: sql_db_list_tables
d|Observation: departments, students, teachers
d|Thought: 我需要先看看有哪些表
d|Action: sql_db_list_tables
d|Observation: departments, students, teachers
d|Thought: 我需要先看看有哪些表
d|Action: sql_db_list_tables
d|Observation: departments, students, teachers
y|... 重复 24 次后触发 max_iterations 上限
r|ValueError: Agent stopped due to iteration limit or time limit.
"""),

    ("stream-garbled-cn", "$ python src/agent/stream_demo.py", """
d|for chunk in agent.stream(...):
d|    print(chunk, end="", flush=True)
d|
r|Hello, 鎴戞槸涓€涓猘I鍔╂墜锛屽彲浠ュ府浣犳煡鏁版嵁搴撱€?
r|锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷
d|
d|（Windows 终端默认 GBK，流式字节被按 GBK 解了）
"""),

    ("api-key-in-git-history", "$ git log --all -S \"sk-\" --oneline", """
d|a3f9c21 fix: 修正模型名
d|7d2e1b0 feat: 接入百炼
d|
r|$ git show 7d2e1b0 -- src/agent/my_llm.py
r|+    api_key="sk-8f3a9c2e4b7d1f6a5c8e2d4b7a1f3e9c"
d|
d|（即使后来删掉了，密钥仍然留在历史里）
"""),

    ("embedding-dimension", "$ python src/rag/build_index.py", """
d|Traceback (most recent call last):
d|  File "src/rag/build_index.py", line 26, in <module>
d|    collection.add(documents=texts, embeddings=vectors)
d|  File "chromadb/api/models/Collection.py", line 178, in add
r|chromadb.errors.InvalidDimensionException:
r|Embedding dimension 1024 does not match collection dimensionality 1536
d|
d|（先用了 text-embedding-3-small，后来换成 bge-large-zh）
"""),

    ("chroma-sqlite-version", "$ python src/rag/build_index.py", """
d|Traceback (most recent call last):
d|  File "src/rag/build_index.py", line 4, in <module>
d|    import chromadb
d|  File "chromadb/__init__.py", line 12, in <module>
d|    from chromadb.api.client import Client
d|  File "chromadb/duckdb.py", line 31, in <module>
d|    import duckdb
r|RuntimeError: Your system has an unsupported version of sqlite3.
r|Chroma requires sqlite3 >= 3.35.0
r|Please note: This is an issue with the Python sqlite3 module,
r|not your system's sqlite3 binary.
"""),

    ("rag-bad-chunking", "$ python src/rag/query.py", """
b|用户: 第三章的截止日期是什么时候？
d|
r|AI: 根据文档，第三章讨论了项目的背景和意义，主要阐述了……
d|
d|命中片段（chunk_size=1500, overlap=0）：
d|  [目录] 第一章 绪论 ........... 1
d|         第二章 需求分析 ........ 5
d|         第三章 系统设计 ........ 9
d|
y|（真正写着日期的段落被切成了碎片，没被检索到）
"""),

    ("tool-description-vague", "$ python src/agent/text_to_sql_agent.py", """
b|用户: 帮我查一下数据库里有多少学生
d|
r|AI: 抱歉，我无法访问你的数据库。
d|
d|工具定义:
d|  name: query
d|  description: "执行查询"
d|
y|（模型不知道什么时候该用它 —— description 等于没说）
"""),

    ("request-timeout", "$ time python src/agent/text_to_sql_agent.py", """
d|（卡在这里没有任何输出）
d|
d|
d|
r|openai.APITimeoutError: Request timed out.
d|
d|real    10m0.342s
y|（默认超时 600 秒，用户干等了十分钟）
"""),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.normpath(os.path.join(here, "..", "images"))
    os.makedirs(outdir, exist_ok=True)
    for name, title, body in SHOTS:
        p = render(name, title, body, outdir)
        print("ok  %-28s %s" % (name, os.path.basename(p)))
    print("\n共 %d 张，输出到 %s" % (len(SHOTS), outdir))


if __name__ == "__main__":
    sys.exit(main())
