import os
import dotenv
import numpy as np
from scipy.spatial.distance import cdist
from pprint import pprint
from langchain_community.chat_models import ChatYandexGPT
from langchain_core.messages import HumanMessage, SystemMessage
import requests
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings.yandex import YandexGPTEmbeddings
from langchain.vectorstores import Chroma
from chromadb.config import Settings

# Два варианта:
# HuggingFaceEmbeddings + YandexGPT - работает корректно,
# YandexEmbeddings + YandexGPT - работает, но только через запрос к Api,
#   а не через langchain (проблема в yandexcloud).
dotenv.load_dotenv()
catalog_id = os.getenv("yandex_catalog_id")
key_id = os.getenv("yandex_key_id")
secret_key = os.getenv("yandex_secret_key")


def langchain_func():
    llm = ChatYandexGPT(api_key=secret_key, model_uri=f"gpt://{catalog_id}/yandexgpt-lite")
    answer = llm.invoke(
        [
            SystemMessage(
                content="You are a helpful assistant that translates English to French."
            ),
            HumanMessage(content="I love programming."),
        ]
    )
    print(answer)


def requests_func():
    prompt = {
        "modelUri": f"gpt://{catalog_id}/yandexgpt-lite",
        "completionOptions":
            {"stream": False,
             "temperature": 0.6},
        "messages": [{"role": "system",
                      "text": "You are a helpful assistant that translates English to French."},
                     {"role": "user", "text": "I love programming."}]
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Api-Key {secret_key}"}
    resp = requests.post(url, headers=headers, json=prompt)
    result = resp.text
    pprint(result)


def request_func_with_context():
    loader = DirectoryLoader(
        r"C:\Users\rybol\PycharmProjects\AIAgentsForSPbSU_News\university_data")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        # chunk_overlap=200,
        separators=[";;"],
    )
    documents = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()
    db = Chroma.from_documents(
        documents,
        embeddings,
        client_settings=Settings(anonymized_telemetry=False),
    )

    question = ("Расскажи о мероприятиях, которые проводит и "
                "к которым имеет отношение компания YADRO")
    docs = db.similarity_search(question, k=3)
    pprint(docs)
    context = ""
    for elem in docs:
        cont_part = elem.page_content
        if cont_part.startswith(";;"):
            cont_part = cont_part[2:]
        context += cont_part.strip() + " "
    pprint(context)

    prompt = {
        "modelUri": f"gpt://{catalog_id}/yandexgpt-lite",  # указание конкретной модели
        "completionOptions":
            {"stream": False,  # потоковая передача частичной генерации
             "temperature": 0.1},  # чем меньше значение, тем меньше вероятность галлюцинаций
        "messages": [{"role": "system",
                      "text": f"В своих ответах ты должен достаточно подробно ответить на вопрос, "
                              f"переданный пользователем. Не цитируй полностью вопрос в своём "
                              f"ответе и не ссылайся напрямую к переданному контексту, "
                              f"но целиком и полностью основывай свой ответ на "
                              f"переданном контексте. Используя данный контекст "
                              f"ответь на вопрос пользователя: {context}"},
                     {"role": "user", "text": f"{question}"}]
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Api-Key {secret_key}"}
    resp = requests.post(url, headers=headers, json=prompt)
    result = resp.text

    return result


def request_yandex_embedding_llm(question: str) -> str:
    doc_uri = f"emb://{catalog_id}/text-search-doc/latest"  # векторизация большого объёма данных
    query_uri = f"emb://{catalog_id}/text-search-query/latest"  # малый объём данных

    embed_url = "https://llm.api.cloud.yandex.net:443/foundationModels/v1/textEmbedding"
    headers = {"Content-Type": "application/json", "Authorization": f"Api-Key {secret_key}",
               "x-folder-id": f"{catalog_id}"}

    doc_texts = [
        """Александр Сергеевич Пушкин (26 мая [6 июня] 1799, Москва — 29 января [10 февраля] 
        1837, Санкт-Петербург) — русский поэт, драматург и прозаик, заложивший основы русского 
        реалистического направления, литературный критик и теоретик литературы, историк, публицист,
         журналист.""",
        """Ромашка — род однолетних цветковых растений семейства астровые, или 
        сложноцветные, по современной классификации объединяет около 70 видов невысоких 
        пахучих трав, цветущих с первого года жизни."""
    ]
    query_text = "когда день рождения Пушкина?"

    # получение эмбеддингов по определённому тексту
    def get_embedding(text: str, text_type: str = "doc") -> np.array:
        query_data = {
            "modelUri": doc_uri if text_type == "doc" else query_uri,
            "text": text,
        }
        # передаётся ссылка на Yandex Api по получению эмбеддингов
        # данные запроса (модель api, непосредственно сам текст который надо обработать)
        # данные для авторизации
        return np.array(requests.post(
            embed_url, json=query_data, headers=headers).json()["embedding"])

    # получение эмбеддингов вопроса
    question = query_text
    quest_embedding = get_embedding(question, text_type="query")
    # получение эмбеддингов базы знаний
    docs_embedding = [get_embedding(doc_text) for doc_text in doc_texts]

    # Вычисляем косинусное расстояние
    dist = cdist(quest_embedding[None, :], docs_embedding, metric="cosine")
    # Вычисляем косинусное сходство
    sim = 1 - dist

    context_document = doc_texts[np.argmax(sim)]
    prompt = {
        "modelUri": f"gpt://{catalog_id}/yandexgpt-lite",
        "completionOptions":
            {"stream": False,
             "temperature": 0.1},
        "messages": [{"role": "system",
                      "text": f"Используя переданный контекст ответь на вопрос пользователя,"
                              f" в ответе не дублируй вопрос и не упоминай слово контекст. "
                              f"Но не забудь добавить, что обозначает твой ответ. "
                              f"Контекст, который необходимо использовать "
                              f"при ответе на вопрос: {context_document}"},
                     {"role": "user", "text": f"{question}"}]
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Api-Key {secret_key}"}
    resp = requests.post(url, headers=headers, json=prompt)
    result = resp.json()["result"]["alternatives"][-1]["message"]["text"]
    return result


if __name__ == "__main__":
    # pprint(request_func_with_context())
    # pprint(request_func_with_context_by_YandexEmbeddings())
    pprint(request_yandex_embedding_llm(""))
