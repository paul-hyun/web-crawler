
import sys, os, argparse, datetime, time, re, collections
import logging
from logging import handlers
logger = logging.getLogger()
import threading, queue
from tqdm import tqdm, trange
import csv
import pandas as pd
import urllib.request as req
from urllib import parse
import bs4
from bs4 import BeautifulSoup


SEPARATOR = u"\u241D"
URL = "https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid1={}&sid2={}&date={}&page={}"
SID = [
    {'sid1': '100', 'sid2': '264', 'name1': '정치', 'name2': '청와대'}, 
    {'sid1': '100', 'sid2': '265', 'name1': '정치', 'name2': '국회/정당'}, 
    {'sid1': '100', 'sid2': '268', 'name1': '정치', 'name2': '북한'}, 
    {'sid1': '100', 'sid2': '266', 'name1': '정치', 'name2': '행정'}, 
    {'sid1': '100', 'sid2': '267', 'name1': '정치', 'name2': '국방/외교'}, 
    {'sid1': '100', 'sid2': '269', 'name1': '정치', 'name2': '정치일반'}, 
    {'sid1': '101', 'sid2': '259', 'name1': '경제', 'name2': '금융'}, 
    {'sid1': '101', 'sid2': '258', 'name1': '경제', 'name2': '증권'}, 
    {'sid1': '101', 'sid2': '261', 'name1': '경제', 'name2': '산업/재계'}, 
    {'sid1': '101', 'sid2': '771', 'name1': '경제', 'name2': '중기/벤처'}, 
    {'sid1': '101', 'sid2': '260', 'name1': '경제', 'name2': '부동산'}, 
    {'sid1': '101', 'sid2': '262', 'name1': '경제', 'name2': '글로벌 경제'}, 
    {'sid1': '101', 'sid2': '310', 'name1': '경제', 'name2': '생활경제'}, 
    {'sid1': '101', 'sid2': '263', 'name1': '경제', 'name2': '경제 일반'}, 
    {'sid1': '102', 'sid2': '249', 'name1': '사회', 'name2': '사건사고'}, 
    {'sid1': '102', 'sid2': '250', 'name1': '사회', 'name2': '교육'}, 
    {'sid1': '102', 'sid2': '251', 'name1': '사회', 'name2': '노동'}, 
    {'sid1': '102', 'sid2': '254', 'name1': '사회', 'name2': '언론'}, 
    {'sid1': '102', 'sid2': '252', 'name1': '사회', 'name2': '환경'}, 
    {'sid1': '102', 'sid2': '59b', 'name1': '사회', 'name2': '인권/복지'}, 
    {'sid1': '102', 'sid2': '255', 'name1': '사회', 'name2': '식품/의료'}, 
    {'sid1': '102', 'sid2': '256', 'name1': '사회', 'name2': '지역'}, 
    {'sid1': '102', 'sid2': '276', 'name1': '사회', 'name2': '인물'}, 
    {'sid1': '102', 'sid2': '257', 'name1': '사회', 'name2': '사회 일반'}, 
    {'sid1': '103', 'sid2': '241', 'name1': '생활문화', 'name2': '건강정보'}, 
    {'sid1': '103', 'sid2': '239', 'name1': '생활문화', 'name2': '자동차/시승기'}, 
    {'sid1': '103', 'sid2': '240', 'name1': '생활문화', 'name2': '도로/교통'}, 
    {'sid1': '103', 'sid2': '237', 'name1': '생활문화', 'name2': '여행/레저'}, 
    {'sid1': '103', 'sid2': '238', 'name1': '생활문화', 'name2': '음식/맛집'}, 
    {'sid1': '103', 'sid2': '376', 'name1': '생활문화', 'name2': '패션/뷰티'}, 
    {'sid1': '103', 'sid2': '242', 'name1': '생활문화', 'name2': '공연/전시'}, 
    {'sid1': '103', 'sid2': '243', 'name1': '생활문화', 'name2': '책'}, 
    {'sid1': '103', 'sid2': '244', 'name1': '생활문화', 'name2': '종교'}, 
    {'sid1': '103', 'sid2': '248', 'name1': '생활문화', 'name2': '날씨'}, 
    {'sid1': '103', 'sid2': '245', 'name1': '생활문화', 'name2': '생활문화 일반'}, 
    {'sid1': '104', 'sid2': '231', 'name1': '세계', 'name2': '아시아/호주'}, 
    {'sid1': '104', 'sid2': '232', 'name1': '세계', 'name2': '미국/중남미'}, 
    {'sid1': '104', 'sid2': '233', 'name1': '세계', 'name2': '유럽'}, 
    {'sid1': '104', 'sid2': '234', 'name1': '세계', 'name2': '중동/아프리카'}, 
    {'sid1': '104', 'sid2': '322', 'name1': '세계', 'name2': '세계 일반'}, 
    {'sid1': '105', 'sid2': '731', 'name1': 'IT/과학', 'name2': '모바일'}, 
    {'sid1': '105', 'sid2': '226', 'name1': 'IT/과학', 'name2': '인터넷/SNS'}, 
    {'sid1': '105', 'sid2': '227', 'name1': 'IT/과학', 'name2': '통신/뉴미디어'}, 
    {'sid1': '105', 'sid2': '230', 'name1': 'IT/과학', 'name2': 'IT 일반'}, 
    {'sid1': '105', 'sid2': '732', 'name1': 'IT/과학', 'name2': '보안/해킹'}, 
    {'sid1': '105', 'sid2': '283', 'name1': 'IT/과학', 'name2': '컴퓨터'}, 
    {'sid1': '105', 'sid2': '229', 'name1': 'IT/과학', 'name2': '게임/리뷰'}, 
    {'sid1': '105', 'sid2': '228', 'name1': 'IT/과학', 'name2': '과학 일반'},
]

DATE_QUEUE = queue.Queue()
THREAD_STATUE = {}
newliles = {
    "br", "div", "p"
}

""" html을 텍스트 형태로 변환 """
def html_to_text(soup):
    for s in soup("script"): # script 제거
        s.extract()
    for s in soup("img"): # image 제거
        s.extract()
    for s in soup("iframe"): # iframe 제거
        s.extract()

    lines = []
    line = []
    for s in soup.descendants:
        if type(s) == bs4.element.NavigableString:
            text = s.strip()
            if 0 < len(text): line.append(text)
        elif s.name in newliles and 0 < len(line):
            lines.append("".join(line).strip())
            line = []
    return "\n".join(lines)


""" 뉴스 텍스트 조회 """
def news_text(opener, news):
    url = news["url"]
    if url.startswith("/"):
        url = f"https://news.naver.com{url}"

    html = opener.open(url)
    soup = BeautifulSoup(html, 'html.parser')

    articleBodyContents = soup.select("#articleBodyContents")
    if len(articleBodyContents) == 0: news["text"] = ""
    else: news["text"] = html_to_text(articleBodyContents[0])
    return news


""" 뉴스 페이지 목록 조회 """
def news_list_item(soup):
    dataset = []
    items = soup.select("#main_content > div.list_body.newsflash_body > ul > li > dl > dt[class!='photo'] > a")
    for item in items:
        url, title = item["href"], item.text.strip()
        if 0 < len(title):
            dataset.append({"url": url, "title": title})
        elif not url.endswith("&page=1"):
            logger.warn(f"zero length: {url} : {item}")
    return dataset


""" 뉴스 페이지 목록 조회 """
def news_list_page(t_id, opener, date, sleep):
    keys = set()
    urls = []
    for sid in SID:
        sid1, sid2, page = sid["sid1"], sid["sid2"], "1"
        key = f"{sid1}.{sid2}.{page}"
        if key not in keys:
            keys.add(key)
            urls.append(URL.format(sid1, sid2, date, page))

    dataset = []
    index = 0
    while index < len(urls):
        url = urls[index]
        html = opener.open(url)
        soup = BeautifulSoup(html, 'html.parser')
        if 0 < sleep: time.sleep(sleep)
        pages = soup.select("#main_content > div.paging > a")
        for page in pages:
            page_url = page["href"]
            query = parse.parse_qs(parse.urlparse(page_url).query)
            sid1, sid2, page = query["sid1"][0], query["sid2"][0], query["page"][0]
            key = f"{sid1}.{sid2}.{page}"
            if key not in keys:
                keys.add(key)
                urls.append(URL.format(sid1, sid2, date, page))
        items = news_list_item(soup)
        dataset.extend(items)

        THREAD_STATUE[t_id] = f"{date}({0:5d}/{len(dataset):5d})"
        # logger.info(f"Url: {url} / Items: {len(items):2d}")           
        index += 1
    return dataset


""" 날짜별로 뉴스 조회 및 저장 """
def crawel_news_date(t_id, args, output, news_set, opener, date):
    dirname = f"{output}/{date[:4]}"
    filename = f"{dirname}/{date}.csv"
    # 이미 수집된 경우는 수집하지 않음
    if os.path.isfile(filename):
        return None
    
    # 뉴스 목록 조회
    news_list = news_list_page(t_id, opener, date, args.sleep)
 
    # 뉴스 내용 조회
    dataset = []
    for i, news in enumerate(news_list):
        url = news["url"]
        query = parse.parse_qs(parse.urlparse(url).query)
        news_id = f"{query['oid'][0]}.{query['aid'][0]}" # oid, aid로 구성된 구분자

        if news_id not in news_set:
            news_set.add(news_id)       
            # 쓰레드 상태 저장
            THREAD_STATUE[t_id] = f"{date}({i:5d}/{len(news_list):5d})"
            # 뉴스 본문 조회
            data = news_text(opener, news)
            if data:
                dataset.append(data)
            # 네이버 ip 블락 방지용 sleep
            if 0 < args.sleep:
                time.sleep(args.sleep)

    # 뉴스저장
    if 0 < len(dataset):
        # 폴더가 존재하지 않을경우 생성
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        df = pd.DataFrame(data=dataset)
        df.to_csv(filename, sep=SEPARATOR, index=False)
    return len(dataset)


""" 스레드 실행 """
def thread_runner(t_id, args, output, news_set):
    global DATE_QUEUE
    THREAD_STATUE[t_id] = ""

    # http request
    opener = req.build_opener()

    zeros = 0
    while zeros < 5 and 0 < DATE_QUEUE.qsize():
        date = DATE_QUEUE.get()
        try:
            time_start = datetime.datetime.now()
            count = crawel_news_date(t_id, args, output, news_set, opener, date)
            if count is not None:
                if 0 < count: zeros = 0
                else: zeros += 1
                time_end = datetime.datetime.now()
                duration = time_end - time_start
                logger.info(f"Thread: {t_id:2d} / Date: {date} / Count: {count:4d} / Time: {duration.total_seconds():6.2f} / Remain: {DATE_QUEUE.qsize():5d}")
        except Exception as ex:
            print(traceback.format_exc())
            logger.info(f"Thread: {t_id:2d} / Date: {date} / Exception: {ex} / Remain: {DATE_QUEUE.qsize():5d}")
    
    del THREAD_STATUE[t_id]


""" 분류별 뉴스 수집 """
def crawel_news(args):
    csv.field_size_limit(sys.maxsize)

    max_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    max_date = max_date - datetime.timedelta(days=1)
    min_date = datetime.datetime.strptime(f"20000101", "%Y%m%d")

    # 날짜를 기준으로 조회할 데이터 범위 결정
    if args.year is not None:
        start_date = datetime.datetime.strptime(f"{args.year}1231", "%Y%m%d")
        if start_date > max_date: start_date = max_date
        end_date = datetime.datetime.strptime(f"{args.year}0101", "%Y%m%d")
        if end_date < min_date: end_date = min_date
    else:
        start_date = max_date
        end_date = min_date
    assert start_date > end_date

    output = f"{args.output}"
    # 뉴스를 저장할 폴더 생성
    if not os.path.isdir(output):
        os.makedirs(output)

    # 조회할 데이터 목록 생성
    while start_date >= end_date:
        DATE_QUEUE.put(start_date.strftime("%Y%m%d"))
        start_date -= datetime.timedelta(days=1)
    
    # crawlled news set
    news_set = set()

    for t_id in range(args.threads):
        thread = threading.Thread(target=thread_runner, args=(t_id, args, output, news_set))
        thread.start()
        time.sleep(0.1)
    
    while 0 < len(THREAD_STATUE):
        time.sleep(10)
        print(THREAD_STATUE, end="\r")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=False,
                        help="뉴스를 크롤링 연도를 입력 합니다. 입력하지 않음면 어제부터 2000년 1월 1일까지 크롤링을 합니다.")
    parser.add_argument("--output", default="naver_news", type=str, required=False,
                        help="뉴스를 저장할 폴더 입니다.")
    parser.add_argument("--threads", default="3", type=int, required=False,
                        help="동시에 실행할 Thread 개수")
    parser.add_argument("--sleep", default="0.01", type=float, required=False,
                        help="초단위 슬립 sleep")
    args = parser.parse_args()

    if not os.path.exists("log"):
        os.makedirs("log")
    
    logger.setLevel(logging.INFO)

    log_handler = handlers.TimedRotatingFileHandler(filename="log/naver_news_csv.log", when="midnight", interval=1, encoding="utf-8")
    log_handler.suffix = "%Y%m%d"
    log_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)8s | %(message)s"))
    logger.addHandler(log_handler)

    crawel_news(args)

