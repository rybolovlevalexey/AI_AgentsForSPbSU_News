import requests
from bs4 import BeautifulSoup
import fake_useragent
import re


def regex_cleaning(text: str) -> str:
    text = re.sub('\xa0', ' ', text)
    text = re.sub('\xad', '', text)
    text = re.sub('\\s+', ' ', text)
    text = re.sub('\\s{2,}', ' ', text)
    text = re.sub(',\\s{1,},', ',', text)
    text = re.sub(' ,', ',', text)
    text = re.sub(':,', ':', text)
    text = re.sub(',,', ',', text)
    text = re.sub(r' \.+', '.', text)
    text = re.sub(r'\.,+', '.', text)
    text = re.sub(r'\.\.+', '.', text)
    # text = re.sub('\u200e', '', text)
    text = re.sub('—,', '—', text)
    text = re.sub('0x98', '', text)
    return text


def news_website_parser(count: int = 20) -> bool:
    BASE_URL = "https://spbu.ru/"
    file = open("../university_data/news_web_site_parsing.txt", "w", encoding="UTF-8")
    parsed_count: int = 0
    for i in range(10):
        url = f"https://spbu.ru/news-events/novosti?page={i}"
        resp = requests.get(url, headers={"User-Agent": fake_useragent.UserAgent().random})
        if int(resp.status_code) != 200:
            continue
        soup = BeautifulSoup(resp.content, "html.parser")
        if soup.find("div", class_="col-xs-12 col-md-9 col-lg-8 card-list--medium "
                                   "card-list--context card-list-clear-sm "
                                   "card-context--clear") is None:
            continue
        for link in soup.find("div", class_="col-xs-12 col-md-9 col-lg-8 card-list--medium "
                                            "card-list--context card-list-clear-sm "
                                            "card-context--clear").find_all(
            "div", recursive=False):
            new_resp = requests.get(BASE_URL + link.find("a").get("href"),
                                    headers={"User-Agent": fake_useragent.UserAgent().random})
            new_soup = BeautifulSoup(new_resp.content, "html.parser")
            res_text = new_soup.find("h1").text + ". "
            if new_soup.find("div", class_="col-xs-12 col-md-9 col-lg-6"
                                                 " col-lg-offset-2 node node-news") is None:
                continue
            for elem in new_soup.find("div", class_="col-xs-12 col-md-9 col-lg-6"
                                                    " col-lg-offset-2 node node-news").find_all(
                ["p", "h2", "h3", "h4", "ul", "ol"]):
                if len(elem.text) == 0:
                    continue
                text_part = ""
                for letter in regex_cleaning(elem.text):
                    if letter.isalnum() or letter in " ,.:;/?!()[]{}-#@_№—=«»":
                        text_part += letter
                if elem.name in ["h2", "h3", "h4"]:
                    if elem.text[-1].isalnum():
                        res_text += text_part + ": "
                    else:
                        res_text += text_part + " "
                elif elem.name == "p":
                    if elem.text[-1].isalnum():
                        res_text += text_part + ". "
                    else:
                        res_text += text_part + " "
                elif elem.name in ["ul", "ol"]:
                    if ("gallery" in elem.get("class", []) or
                            "js-gallery" in elem.get("class", [])):
                        continue
                    res_text += "; ".join(["".join(list(filter(
                        lambda let: let.isalnum() or let in " ,.:;/?!()[]{}-#@_№—=«»",
                        list(line.text)))) for line in elem.find_all("li")]) + ". "
            res_text = regex_cleaning(res_text) + ";; \n"
            file.writelines([res_text])
            parsed_count += 1
            if parsed_count >= count:
                file.close()
                return True
    file.close()
    return False


if news_website_parser(count=50):
    print("news site done")