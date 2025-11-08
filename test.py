from dotenv import load_dotenv
import os
from openai import OpenAI


def make_client() -> OpenAI:
    load_dotenv()

    api_key = os.getenv("ARK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("ARK_API_KEY or OPENAI_API_KEY not found in .env")

    base_url = os.getenv("OPENAI_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

    print("Using base_url:", base_url)   # 调试用，可以看到真实地址
    return OpenAI(api_key=api_key, base_url=base_url)
def main() -> None:
    client = make_client()

    resp = client.chat.completions.create(
        model="ep-20251108134917-mcjqk",   # 先按你截图里的接入点 ID 写
        messages=[{
            "role": "user",
            "content": (
                "Please introduce yourself in one short sentence and say "
                "that you are called through VolcEngine Ark DeepSeek-R1."
            ),
        }],
        max_tokens=128,
    )

    print(resp.choices[0].message.content)


if __name__ == "__main__":
    main()
