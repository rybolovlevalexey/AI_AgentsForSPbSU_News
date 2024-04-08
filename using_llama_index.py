import os
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from langchain.vectorstores import Chroma
from llama_index.core import GPTVectorStoreIndex
from llama_index.core import VectorStoreIndex
from llama_index.llms.llama_api import LlamaAPI
import openai
import dotenv


dotenv.load_dotenv()
llama = LlamaAPI(api_key=os.getenv("llama_api_token"))
resp = llama.complete("Albert Einstein is ")
print(resp)

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