import os
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from langchain.vectorstores import Chroma
from llama_index.core import GPTVectorStoreIndex
from llama_index.core import VectorStoreIndex
import openai
import dotenv


# Не забываем указать ключ к апи
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

reader = SimpleDirectoryReader(input_dir='./university_data/')
docs = reader.load_data()
print(f'Loaded {len(docs)} docs')

# parser = SimpleNodeParser()
# nodes = parser.get_nodes_from_documents(docs)
# print(len(nodes))

# Создаем индекс
index = VectorStoreIndex.from_documents(docs)
# Индексируем ноды
# index.insert_nodes(nodes)

# Создаем движок запросов
engine = index.as_query_engine()
# Пробуем задать вопрос
question = ""
response = engine.query(question)
print(response)