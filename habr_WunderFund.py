import os

import openai
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter


def load_and_split_documents() -> list[dict]:
    """
    Загружает наши документы с диска и разбивает их на фрагменты.
    Возвращает список словарей.
    """
    # Загрузка данных.
    loader = DirectoryLoader(
        DATA_DIR, loader_cls=UnstructuredMarkdownLoader, show_progress=True
    )
    docs = loader.load()

    # Разбиение документов на фрагменты.
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN, chunk_size=6000, chunk_overlap=100
    )
    split_docs = splitter.split_documents(docs)

    # Преобразование документов в список словарей.
    final_docs = []
    for i, doc in enumerate(split_docs):
        doc_dict = {
            "id": str(i),
            "content": doc.page_content,
            "sourcefile": os.path.basename(doc.metadata["source"]),
        }
        final_docs.append(doc_dict)

    return final_docs
