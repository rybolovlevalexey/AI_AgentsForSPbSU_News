# from snscrape.modules.telegram import Channel, TelegramChannelScraper
# from snscrape.modules.vkontakte import VKontakteUserScraper
# import re
# from telethon.client import TelegramClient
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime, date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def dynamic_site_read(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    while True:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        if element:
            page_source = driver.page_source
            driver.quit()
            break
    return page_source


def tg_parser(chanel_name: str = "spbuniversity1724", limit_count: int = 10) -> list[dict[str, str]]:
    posts_text: list[dict[str, str]] = list()
    url: str = f"https://t.me/s/{chanel_name}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    # последний пост в канале на данный момент
    last_post = soup.find_all(class_="tgme_widget_message_wrap js-widget_message_wrap")[-1]
    last_id = last_post.find("div").get("data-post").split("/")[1]
    finish_id = int(last_id) - limit_count
    if finish_id < 0:
        finish_id = 0

    for iter_id in range(int(last_id), 0, -1):
        try:
            post_soup = BeautifulSoup(dynamic_site_read(
                f"https://t.me/{chanel_name}/{iter_id}"), "html.parser")
        except:
            continue
        if post_soup.find("iframe") is None:
            print(f"https://t.me/{chanel_name}/{iter_id}")
            continue
        src_url = post_soup.find("iframe").get("src")
        post_soup_closer = BeautifulSoup(dynamic_site_read(src_url), "html.parser")
        if post_soup_closer.find(class_="tgme_widget_message_text js-message_text"):
            text_part = ""
            post_tag_text = post_soup_closer.find(
                class_="tgme_widget_message_text js-message_text").get_text()
            post_tag_text = post_tag_text.replace("\n", " ")
            for letter in post_tag_text:
                if letter.isalnum() or letter in " ,.:;/?!()[]{}-#@_":
                    text_part += letter
            if post_soup_closer.find("time") and post_soup_closer.find("time").get("datetime"):
                post_date = post_soup_closer.find("time").get("datetime").split("T")[0]
            else:
                post_date = None
            if (text_part + ";; \n") not in list(map(lambda elem: elem["text"], posts_text)):
                posts_text.append({"text": text_part + ";; \n", "source": "tg",
                                   "parsing_date": str(date.today()),
                                   "post_date": post_date, "url": src_url})
            if len(posts_text) >= limit_count:
                break
    with open("../university_data/tg_parsing.txt", "w", encoding="utf-8") as file:
        file.writelines(list(map(lambda elem: elem["text"], posts_text)))
    return posts_text


tg_parser(limit_count=30)
print("tg done")