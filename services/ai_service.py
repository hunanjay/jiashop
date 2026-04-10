import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM with Qwen (OpenAI Compatible)
# Read local QWEN_ specific environment variables
model_name = os.getenv("QWEN_MODEL", "qwen3.5-flash")
api_key = os.getenv("QWEN_API_KEY")
api_base = os.getenv("QWEN_API_BASE")

llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    openai_api_base=api_base,
    temperature=0.7,
)

# System Prompt for GiftCraft
system_prompt = """你是 GiftCraft 礼品定制店的智能客服。
你了解店内所有商品，帮助用户找到合适的定制礼品。
回复要友好、专业，控制在150字以内。"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# Create the LCEL chain
# Chain = Prompt | LLM | StrOutputParser
chain = prompt | llm | StrOutputParser()

def get_ai_response(user_input: str):
    """Simple synchronous call"""
    return chain.invoke({"input": user_input})

def stream_ai_response(user_input: str):
    """Streaming call"""
    return chain.stream({"input": user_input})
