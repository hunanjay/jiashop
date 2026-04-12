import os
import httpx
from langchain_openai import ChatOpenAI


def get_llm():
    """获取统一配置的 Qwen LLM 实例"""
    # 优先从环境变量读取，默认使用验证过的 qwen-plus
    model_name = os.getenv("QWEN_MODEL", "qwen3.5-flash")
    api_key = os.getenv("QWEN_API_KEY")
    api_base = os.getenv(
        "QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    print(f"DEBUG: Initializing LLM with Model={model_name}, Base={api_base}")

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        openai_api_base=api_base,
        http_client=httpx.Client(verify=False),  # 跳过 SSL/Hostname 验证
        temperature=0.7,
        streaming=True,  # 开启流式输出，实现打字机效果
    )


# 默认导出实例
llm = get_llm()
