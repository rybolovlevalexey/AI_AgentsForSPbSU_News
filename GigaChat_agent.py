from langchain_community.chat_models import GigaChat
from langchain_community.document_loaders import TextLoader  # для загрузки документа с новостями
from langchain.text_splitter import RecursiveCharacterTextSplitter  # для разбиения текста
from langchain_community.vectorstores import FAISS  # векторная база данных
from langchain_openai import OpenAIEmbeddings  # для векторизации текста
from langchain.tools.retriever import create_retriever_tool  # для создания ретривер-инструмента

from typing import Any, Coroutine, List
import datasets
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from pprint import pprint
from dotenv import load_dotenv
import os
# from gigachain-community.embeddings import HuggingFaceEmbeddings
load_dotenv()


class HuggingFaceE5Embeddings(HuggingFaceEmbeddings):
    def embed_query(self, text: str) -> List[float]:
        text = f"query: {text}"
        return super().embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        texts = [f"passage: {text}" for text in texts]
        return super().embed_documents(texts)

    async def aembed_query(self, text: str) -> Coroutine[Any, Any, List[float]]:
        text = f"query: {text}"
        return await super().aembed_query(text)

    async def aembed_documents(
        self, texts: List[str]
    ) -> Coroutine[Any, Any, List[List[float]]]:
        texts = [f"passage: {text}" for text in texts]
        return await super().aembed_documents(texts)


ds = datasets.load_dataset("university_data")
print(type(ds))
print(ds)
documents = [
    Document(page_content=context) for context in set(ds)
]
embedding = HuggingFaceE5Embeddings(model_name="intfloat/multilingual-e5-base")
print("here1")
faiss_db = FAISS.from_documents(documents, embedding=embedding)
print("here2")
embedding_retriever = faiss_db.as_retriever(search_kwargs={"k": 5})
print("here3")
print(embedding_retriever.get_relevant_documents("посол из Бразилии в СПбГУ"))
