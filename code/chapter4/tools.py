from dotenv import load_dotenv
load_dotenv()

import os
import serpapi
from typing import Dict, Any


# 使用新版 serpapi Python SDK 的兼容封装
class SerpApiClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("SERPAPI_API_KEY is not set")
        # 新版 SDK 的客户端
        self.client = serpapi.Client(api_key=api_key)

    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """返回 SerpApi 原始结果字典，方便外面做各种解析。"""
        params = {
            "engine": "google",
            "q": query,
            "num": num_results,
            # 可以按需加 location / hl / gl 等参数
        }
        return self.client.search(params)


# 全局初始化一个 client（如果没配置 key，就置为 None）
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
serp_client: "SerpApiClient | None"
if SERPAPI_API_KEY:
    serp_client = SerpApiClient(SERPAPI_API_KEY)
else:
    serp_client = None
    print("⚠️ 警告：SERPAPI_API_KEY 未在 .env 中配置，搜索工具将不可用。")


def search(query: str) -> str:
    """
    一个基于 SerpApi 的实战网页搜索引擎工具。
    它会智能地解析搜索结果，优先返回直接答案或知识图谱信息。
    """
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        if serp_client is None:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"

        # 调用我们封装好的 client，拿到完整结果
        results = serp_client.search(query)

        # 智能解析：优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer_box" in results:
            answer_box = results["answer_box"]
            if isinstance(answer_box, dict) and "answer" in answer_box:
                return answer_box["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)

        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")

        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        return "\n".join(
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        )


# --- 工具初始化与使用示例 ---
if __name__ == "__main__":
    # 1. 初始化工具执行器
    toolExecutor = ToolExecutor()

    # 2. 注册我们的实战搜索工具
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)

    # 3. 打印可用的工具
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    # 4. 智能体的 Action 调用，这次我们问一个实时性的问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误：未找到名为 '{tool_name}' 的工具。")
