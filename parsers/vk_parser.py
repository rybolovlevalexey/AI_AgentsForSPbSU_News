# https://<адрес-сервера>/method/<имя-API-метода>?<параметры>
import os
from typing import Union
import requests
from pprint import pprint
import dotenv
import json
from datetime import date, datetime

dotenv.load_dotenv()
VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")


def vk_parser(chanel_name: str = "mmspbu", method_name: str = "wall.get",
              count: int = 10, file_name_as_chanel: bool = False) \
        -> Union[list[dict[str, str]], False]:
    # chanel_name = "spbucareer"
    posts_splitter = ";; \n"
    url: str = f"https://api.vk.ru/method/{method_name}?v=5.199HTTP/1.1&domain={chanel_name}"
    if count is not None:
        url += f"&count={str(count)}"

    auth_header = {"Authorization": f"Bearer {VK_ACCESS_TOKEN}"}
    resp = requests.get(url, headers=auth_header)
    text_lines: list[dict[str, str]] = list()
    for item in json.loads(resp.content.decode("utf-8"))["response"]["items"]:
        text_part = ""
        for letter in item["text"]:
            if letter.isalnum() or letter in " ,.:;/?!()[]{}-#@_№—=«»":
                text_part += letter
            elif letter == "\n":
                text_part += " "
        while "  " in text_part:
            text_part = text_part.replace("  ", " ")
        if " ." in text_part:
            text_part = text_part.replace(" .", ".")

        text_lines.append({"text": text_part.strip() + posts_splitter, "source": "vk",
                           "parsing_date": str(date.today()),
                           "post_date": datetime.fromtimestamp(item["date"]).strftime('%Y-%m-%d')})
    if not file_name_as_chanel:
        with open("../university_data/vk_parsing.txt", "w", encoding="utf-8") as file:
            file.writelines(list(map(lambda elem: elem["text"], text_lines)))
    else:
        with open(f"../university_data/{chanel_name}_vk_parsing.txt",
                  "w", encoding="utf-8") as file:
            file.writelines(list(map(lambda elem: elem["text"], text_lines)))
    return text_lines


vk_parser(chanel_name="spbu_internship", count=50, file_name_as_chanel=True)
print("vk done")