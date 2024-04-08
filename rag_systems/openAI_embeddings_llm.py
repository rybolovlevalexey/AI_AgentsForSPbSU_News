import os
import wget
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import BSHTMLLoader
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.chains import RetrievalQA
import dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# Скорее всего самый бесперспективный вариант. Т.к. нет доступа к OpenAI api key.
# OpenAI Embeddings + ChatGPT не работает из-за отсутствия api key.
# Возможно удастся решить эту проблему, в противном случае можно удалить.
dotenv.load_dotenv()
chat_gpt = ChatOpenAI()
messages = [
    SystemMessage(content=("Ты профессор истории искусств, который описывает "
                  "в молодёжном сленге популярных исполнителей")),
    HumanMessage(content="Кто такой Eminem?")
]
chat_gpt.invoke(messages)
result = chat_gpt.invoke(messages)
print(result)

# load text from html
# loader = BSHTMLLoader("text_0073.shtml", open_encoding='ISO-8859-1')
# war_and_peace = loader.load()
loader = DirectoryLoader("./university_data")
spbu_news_data = loader.load()
print("loader ready")

# init Vector DB
# embeddings = OpenAIEmbeddings()
embeddings = HuggingFaceEmbeddings()
print("embeddings ready")

doc_store = Qdrant.from_documents(
    spbu_news_data,
    embeddings,
    location=":memory:",
    collection_name="docs",
)
print("database ready")

llm = OpenAI()

while True:
    question = input('Ваш вопрос: ')
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=doc_store.as_retriever(),
        return_source_documents=False,
    )

    result = qa(question)
    print(f"Answer: {result}")