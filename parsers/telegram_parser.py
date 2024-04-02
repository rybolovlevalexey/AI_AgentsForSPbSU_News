from snscrape.modules.telegram import Channel, TelegramChannelScraper
from snscrape.modules.vkontakte import VKontakteUserScraper
import re

api_id = 25747007
api_hash = "c12140719698e4ec454f50ae9c1eda06"


def tg_func():
    # https://t.me/spbuniversity1724
    tg_parser = TelegramChannelScraper("spbuniversity1724")
    tg_lines = list()

    for elem in tg_parser.get_items():
        if elem.content is None:
            continue
        text_part = ""
        for letter in elem.content:
            if letter.isalnum() or letter in " ,.:;/?!()[]{}-":
                text_part += letter

        tg_lines.append(text_part + ";; \n")
    with open("../university_data/tg_parsing.txt", "w", encoding="utf-8") as file:
        file.writelines(tg_lines)
    return True


def vk_func():
    # https://vk.com/mmspbu
    vk_parser = VKontakteUserScraper("mmspbu")
    print(*vk_parser.get_items())
    for elem in vk_parser.get_items():
        print(elem.url)


print(tg_func())