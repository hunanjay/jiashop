from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .mcp.model import llm

# 系统提示词 (无 RAG 版本，不调用 Embedding API)
PROMPT_TEMPLATE = """你是 GiftCraft 礼品店的智能客服 JiaJia。
你的任务是为用户提供专业的礼品推荐、解答商品疑问，并协助查询订单。
请使用亲切、专业的语气回答，适当使用 Emoji 使对话更生动。"""

customer_prompt = ChatPromptTemplate.from_messages([
    ("system", PROMPT_TEMPLATE),
    ("human", "{input}"),
])

def get_customer_care_chain():
    """获取客服 Chain（纯 LLM 对话，不调用 Embedding API）"""
    return customer_prompt | llm | StrOutputParser()
