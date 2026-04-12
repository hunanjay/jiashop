import os
import httpx
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from db.models import Product


def get_product_retriever():
    """从数据库加载商品数据并构建本地向量库检索器"""
    products = Product.query.filter_by(status="active").all()
    if not products:
        return None

    docs = []
    for p in products:
        content = f"商品: {p.name}\n分类: {p.category}\n价格: {p.price}元\n描述: {p.description}"
        docs.append(Document(page_content=content, metadata={"id": p.id}))

    # 从环境变量读取分词/向量模型名，默认使用 text-embedding-v2
    embeddings = OpenAIEmbeddings(
        model=os.getenv("QWEN_EMBEDDING_MODEL"),
        api_key=os.getenv("QWEN_API_KEY"),
        openai_api_base=os.getenv("QWEN_API_BASE"),
        http_client=httpx.Client(verify=False),
    )

    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 3})
