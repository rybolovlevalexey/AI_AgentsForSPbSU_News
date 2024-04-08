import os
from langchain.document_loaders import TextLoader, DirectoryLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import dotenv
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_community.embeddings.huggingface import (HuggingFaceEmbeddings,
                                                        HuggingFaceBgeEmbeddings,
                                                        HuggingFaceInstructEmbeddings,
                                                        HuggingFaceInferenceAPIEmbeddings)
from langchain_community.embeddings.bookend import BookendEmbeddings
from langchain_community.embeddings.yandex import YandexGPTEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.chat_models import GigaChat
from langchain.schema import HumanMessage
from pprint import pprint

# Эталонный вариант. HuggingFaceEmbeddings + GigaChat.
# Находит необходимые документы и корректно отвечает на вопросы
dotenv.load_dotenv()
llm = GigaChat(credentials=os.getenv("GigaChat_credentials"), verify_ssl_certs=False)

loader = DirectoryLoader(r"C:\Users\rybol\PycharmProjects\AIAgentsForSPbSU_News\university_data")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    # chunk_overlap=200,
    separators=[";;"],
)
documents = text_splitter.split_documents(documents)
print(f"Total documents: {len(documents)}")
# pprint(documents)

# embeddings = GigaChatEmbeddings(credentials=os.getenv("GigaChat_credentials"))
embeddings = HuggingFaceEmbeddings()
# folder_id = "b1go3kphb9455mmm06rb"
# embeddings = YandexGPTEmbeddings(model_uri=f"gpt://{folder_id}/yandexgpt-lite/latest")
print("start making database")
db = Chroma.from_documents(
    documents, embeddings,
    client_settings=Settings(anonymized_telemetry=False),
)
print("making database done")

# question = "Семинар от кампании YADRO"
# docs = db.similarity_search(question, k=3)
# pprint(docs)

qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())
while True:
    print("Введите ваш вопрос: ")
    question = input()
    pprint(qa_chain({"query": question}))