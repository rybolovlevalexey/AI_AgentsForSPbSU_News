from langchain_community.chat_models import GigaChat
from langchain.schema import HumanMessage
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.embeddings import GigaChatEmbeddings

from pprint import pprint
from dotenv import load_dotenv
import os


load_dotenv()
chat_model = GigaChat(credentials=os.getenv("GigaChat_credentials"), verify_ssl_certs=False)

loader = TextLoader("parsed_data.txt", encoding="utf-8")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
documents = text_splitter.split_documents(documents)

embeddings = GigaChatEmbeddings(credentials=os.getenv("GigaChat_credentials"))

db = Chroma.from_documents(
    documents,
    embeddings,
    client_settings=Settings(anonymized_telemetry=False))

print()

# question = "Расскажи новости о праздновании монгольского нового года. "
# pprint(chat_model.invoke([HumanMessage(content=question)]).content)
