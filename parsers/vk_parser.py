# https://<адрес-сервера>/method/<имя-API-метода>?<параметры>
import os
from typing import Union
import requests
from pprint import pprint
import dotenv
import json

dotenv.load_dotenv()
VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")
method_name = "wall.get"
chanel_name = "mmspbu"
url: str = f"https://api.vk.ru/method/{method_name}?v=5.199HTTP/1.1&domain={chanel_name}"
count: Union[int, None] = 15
if count is not None:
    url += f"&count={str(count)}"

auth_header = {"Authorization": f"Bearer {VK_ACCESS_TOKEN}"}
resp = requests.get(url, headers=auth_header)
text_lines: list[str] = list()
for item in json.loads(resp.content.decode("utf-8"))["response"]["items"]:
    text_part = ""
    for letter in item["text"]:
        if letter.isalnum() or letter in " ,.:;/?!()[]{}-":
            text_part += letter
    text_lines.append(text_part.strip() + ";; \n")
with open("../university_data/vk_parsing.txt", "w", encoding="utf-8") as file:
    file.writelines(text_lines)
