from langchain_community.chat_models import GigaChat
from langchain_community.document_loaders import TextLoader  # для загрузки документа с новостями
from langchain.text_splitter import RecursiveCharacterTextSplitter  # для разбиения текста
from langchain_community.vectorstores import FAISS  # векторная база данных
from langchain_openai import OpenAIEmbeddings  # для векторизации текста
from langchain.tools.retriever import create_retriever_tool  # для создания ретривер-инструмента

from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv()


def main():  # в теории должно работать, если получится нормально запустить создание Embeddings
    loader = TextLoader("parsed_data.txt", encoding="utf-8")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(documents)
    print("here1")
    vector = FAISS.from_documents(documents, OpenAIEmbeddings(
        openai_api_key=os.getenv("Openai_api_key")))
    # вот тут происходит ошибка (наверное, из-за api key
    print("here2")

    retriever = vector.as_retriever()
    result = retriever.similarity_search_with_score("новость про монгольский новый год")
    print(result)

    retriever_tool = create_retriever_tool(
        retriever,
        "news_from_document_retriever",
        "it will return news from a document based on the St. "
        "Petersburg State University website",
    )

    # создание агента
    chat_model = GigaChat(credentials=os.getenv("GigaChat_credentials"),
                          verify_ssl_certs=False, temperature=0)
