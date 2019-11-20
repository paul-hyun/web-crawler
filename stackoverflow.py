import sys, os, argparse, datetime, time, re, collections
import logging
from logging import handlers
logger = logging.getLogger()
import urllib.request as req
from urllib import parse
import bs4
from bs4 import BeautifulSoup
import pandas as pd


SEPARATOR = u"\u241D"
URL = "https://stackoverflow.com/questions/tagged/{}?tab=votes&page={}&pagesize=50"


def stackoverflow_list_page(opener, tag, sleep):
    dataset = []
    for page in range(1, 999999):
        url = URL.format(tag, page)
        print(url)
        html = opener.open(url)
        soup = BeautifulSoup(html, 'html.parser')
        if 0 < sleep: time.sleep(sleep)
        questions = soup.select("#questions > div.question-summary")
        for question in questions:
            votes = question.select("div.statscontainer > div.stats > div.vote > div > span > strong")[0].text.strip()
            answer = question.select("div.statscontainer > div.stats > div.status > strong")[0].text.strip()
            items = question.select("div.summary > h3 > a")
            title = items[0].text.strip()
            url = items[0]["href"]
            overview = question.select("div.summary > div.excerpt")[0].text.strip()
            items = question.select("div.summary > div.tags > a")
            tags = []
            for item in items:
                tags.append(item.text.strip())
            act_time = question.select("div.summary > div.started.fr > div > div.user-action-time > span")[0]["title"]
            items = question.select("div.summary > div.started.fr > div > div.user-gravatar32 > a > div > img")
            user_img = items[0]["src"] if items else ""
            user_id = question.select("div.summary > div.started.fr > div > div.user-details")[0].text.strip()
            items = question.select("div.summary > div.started.fr > div > div.user-details > a")
            user_home = items[0]["href"] if items else ""
            row = {
                "votes": votes,
                "answer": answer,
                "title": title,
                "url": url,
                "overview": overview,
                "tags": str(tags),
                "act_time": act_time,
                "user_img": user_img,
                "user_id": user_id,
                "user_home": user_home,
            }
            dataset.append(row)
        # next page가 없으면 종료
        next = soup.select("#mainbar > div.pager.fl > a > span.next")
        if not next:
            break
    return dataset


def crawel_stackoverflow(args):
    # http request
    opener = req.build_opener()

    dataset = stackoverflow_list_page(opener, args.tag, args.sleep)
    # 저장
    if 0 < len(dataset):
        dirname = f"{args.output}"
        filename = f"{dirname}/deep-learning.csv"
        # 폴더가 존재하지 않을경우 생성
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        df = pd.DataFrame(data=dataset)
        df.to_csv(filename, sep=SEPARATOR, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="stackoverflow", type=str, required=False,
                        help="크로링 데이터를 저장할 폴더 입니다.")
    parser.add_argument("--tag", default="deep-learning", type=str, required=False,
                        help="Stackoverflow tag 입니다.")
    parser.add_argument("--sleep", default="5", type=float, required=False,
                        help="초단위 슬립 sleep")
    args = parser.parse_args()

    if not os.path.exists("log"):
        os.makedirs("log")
    
    logger.setLevel(logging.INFO)

    log_handler = handlers.TimedRotatingFileHandler(filename="log/stackoverflow.log", when="midnight", interval=1, encoding="utf-8")
    log_handler.suffix = "%Y%m%d"
    log_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)8s | %(message)s"))
    logger.addHandler(log_handler)

    crawel_stackoverflow(args)

