# llm_client.py
from dotenv import load_dotenv
import os
from openai import OpenAI


class HelloAgentsLLM:
    """
    Hello-Agents 项目里的统一 LLM 封装。
    这里我们改成走「火山方舟 DeepSeek-R1 的 OpenAI 兼容接口」。
    """

    def __init__(self, model_id: str | None = None,
                 api_key: str | None = None,
                 base_url: str | None = None):
        """
        初始化 LLM 客户端。
        优先级：显式参数 > .env 变量 > 默认值。
        """
        load_dotenv()

        # 1. 模型 ID：优先用传进来的，其次用环境变量，最后用默认值
        self.model_id = (
            model_id
            or os.getenv("HELLO_AGENTS_MODEL_ID")
            or os.getenv("MODEL_ID")
            or "ep-20251108134917-mcjqk"  # 你的 DeepSeek-R1 接入点 ID
        )

        # 2. API Key：从 Ark / OpenAI 兼容变量里拿
        self.api_key = (
            api_key
            or os.getenv("ARK_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        # 3. Base URL：火山方舟 OpenAI 协议网关
        self.base_url = (
            base_url
            or os.getenv("OPENAI_BASE_URL")
            or "https://ark.cn-beijing.volces.com/api/v3"
        )

        if not (self.model_id and self.api_key and self.base_url):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        # 创建 OpenAI 兼容客户端（底层其实打到火山方舟）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        一个简单的对话接口：
        - messages: OpenAI 风格的 messages 列表
        - 返回：模型生成的文本
        """
        resp = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            **kwargs,
        )
        return resp.choices[0].message.content

    def think(self, messages: list[dict], **kwargs) -> str:
        """
        ReAct Agent 调用的思考接口。
        这里直接复用 chat 的逻辑即可。
        """
        return self.chat(messages, **kwargs)
        
    def __call__(self, messages: list[dict], **kwargs) -> str:
        """
        让实例本身也可以像函数一样被调用：
        llm([...]) 相当于 llm.chat([...])
        """
        return self.chat(messages, **kwargs)
