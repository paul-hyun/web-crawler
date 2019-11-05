
import os, argparse, datetime, time, re
from tqdm import tqdm, trange
import pandas as pd
import urllib.request as req
from urllib import parse
from bs4 import BeautifulSoup


SEPARATOR = u"\u241D"
URL = "https://news.naver.com/main/list.nhn?mode=LPOD&mid=sec&oid={}&listType=title&date={}"
OIDS = {
    'khan':'032', # 경향신문
    'kmib':'005', # 국민일보
    'donga':'020', # 동아일보
    'munhwa':'021', # 문화일보
    'seoul':'081', # 서울신문
    'segye':'022', # 세계일보
    'chosun':'023', # 조선일보
    'joins':'025', # 중앙일보
    'hani':'028', # 한겨레
    'hankook':'469' # 한국일보
}


""" 뉴스 컨텐츠 조회 """
def news_contents(opener, news):
    url = news["url"]
    if url.startswith("/"):
        url = f"https://news.naver.com{url}"

    html = opener.open(url)
    soup = BeautifulSoup(html, 'html.parser')

    for br in soup.find_all("br"):
        br.replace_with("\n")
    contents = soup.select("#articleBodyContents", text=True)
    if len(contents) == 0: return []
    contents = contents[0].text
    # 제거되지 않는 특수문자 제거
    contents = re.sub(r'//.+', '', contents)
    contents = re.sub(r'function.+', '', contents)
    # 라인단위로 나누어 빈 라인은 제거
    lines = contents.split('\n')
    values = []
    index = None
    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            values.append(line)
            # 다. 형태로 끝나는 부분을 끝으로 인식
            if line.endswith("다."):
                index = len(values)
    
    if 0 < len(values) and index is not None:
        contents = "\n".join(values[:index])
        news["contents"] = contents
        return news
    else: # 본문이 없는 기사
        return None


""" 뉴스 페이지 목록 조회 """
def news_list_item(url, soup):
    dataset = []
    items = soup.select("#main_content > div.list_body.newsflash_body > div.newspaper_area > ul > li > dl > dt > a")
    for item in items:
        url, title = item["href"], item.text.strip()
        if 0 < len(title):
            dataset.append({"url": item["href"], "title": title})
    items = soup.select("#main_content > div.list_body.newsflash_body > ul[class='type02'] > li > a")
    for item in items:
        url, title = item["href"], item.text.strip()
        if 0 < len(title):
            dataset.append({"url": item["href"], "title": title})
    return dataset


""" 뉴스 페이지 목록 조회 """
def news_list_page(opener, oid, date, sleep):
    dataset = []
    url = URL.format(oid, date)
    html = opener.open(url)
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.select("#main_content > div.paging > a")
    dataset.extend(news_list_item(url, soup))
    for page in pages:
        # 네이버 ip 블락 방지용 sleep
        if 0 < sleep:
            time.sleep(sleep)
        url = page["href"]
        if url.startswith("?mode="):
            url = f"https://news.naver.com/main/list.nhn{url}"
        html = opener.open(url)
        soup = BeautifulSoup(html, 'html.parser')
        dataset.extend(news_list_item(url, soup))
    return dataset


""" 날짜별로 뉴스 조회 및 저장 """
def crawel_news_date(args, output, news_set, opener, date):
    dirname = f"{output}/{date[:4]}"
    filename = f"{dirname}/{date}.csv"
    # 이미 수집된 경우는 수집하지 않음
    if os.path.isfile(filename):
        return
    # 폴더가 존재하지 않을경우 생성
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    
    # 뉴스 목록 조회
    news_list = news_list_page(opener, OIDS[args.oid], date, args.sleep)

    # 뉴스 내용 조회
    dataset = []
    for news in news_list:
        url = news["url"]
        query = parse.parse_qs(parse.urlparse(url).query)
        news_id = f"{query['oid'][0]}.{query['aid'][0]}" # oid, aid로 구성된 구분자
        # 이미 조회한 경우는 제외 함
        if news_id not in news_set:
            news_set.add(news_id)
            contents = news_contents(opener, news)
            if contents:
                dataset.append(contents)
            # 네이버 ip 블락 방지용 sleep
            if 0 < args.sleep:
                time.sleep(args.sleep)
    # 뉴스저장
    if 0 < len(dataset):
        df = pd.DataFrame(data=dataset)
        df.to_csv(filename, sep=SEPARATOR, index=False)
    return len(dataset)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--oid", type=str, required=True,
                        help="뉴스를 조화할 얼론사 입니다. [khan(경향신문), kmib(국민일보), donga(동아일보), munhwa(문화일보), seoul(서울신문), segye(세계일보), chosun(조선일보), joins(중앙일보), hani(한겨레), hankook(한국일보)]")
    parser.add_argument("--year", type=int, required=False,
                        help="뉴스를 크롤링 연도를 입력 합니다. 입력하지 않음면 오늘부터 2004년 4월 20일까지 크롤링을 합니다.")
    parser.add_argument("--output", default="naver_news", type=str, required=False,
                        help="뉴스를 저장할 폴더 입니다.")
    parser.add_argument("--sleep", default="0.01", type=float, required=False,
                        help="네이버 ip 블락 방지용 sleep")
    args = parser.parse_args()

    assert args.oid in OIDS

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

    output = f"{args.output}/{args.oid}"
    # 뉴스를 저장할 폴더 생성
    if not os.path.isdir(output):
        os.makedirs(output)

    # 조회할 데이터 목록 생성
    dates = []
    while start_date >= end_date:
        dates.append(start_date.strftime("%Y%m%d"))
        start_date -= datetime.timedelta(days=1)
    
    # http request
    opener = req.build_opener()
    # crawlled news set
    news_set = set()

    zeros = 0
    with tqdm(total=len(dates), desc=f"Crawlling") as pbar:
        for i, date in enumerate(dates):
            pbar.set_postfix_str(f"date: {date}")
            count = crawel_news_date(args, output, news_set, opener, date)
            pbar.update(1)
            if 0 < count:
                zeros = 0
            else:
                zeros += 1
                if 6 < zeros:
                    break
                


