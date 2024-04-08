from pprint import pprint
from langchain_community.chat_models import ChatYandexGPT
from langchain_core.messages import HumanMessage, SystemMessage
import requests
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from chromadb.config import Settings


catalog_id = "b1go3kphb9455mmm06rb"
key_id = "ajer9qh7h0amceu16slc"
secret_key = "AQVN206ieIFWY7wTcqy_4_97yx2D1BYi0pklHeCr"


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


if __name__ == "__main__":
    pprint(request_func_with_context())
