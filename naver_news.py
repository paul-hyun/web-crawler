
import os, argparse, datetime, time, re
from tqdm import tqdm, trange
import pandas as pd
import urllib.request as req
from urllib import parse
from bs4 import BeautifulSoup


SEPARATOR = u"\u241D"
popular_day_url = "https://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&sectionId={}&date={}"
popular_memo_url = "https://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_memo&sectionId={}&date={}"
sections = {'정치':100, '경제':101, '사회':102, '생활문화':103, '세계':104, 'IT과학':105}


""" 뉴스 컨텐츠 조회 """
def news_contents(opener, url):
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
    return [] if index is None else values[:index]


""" 많이본 뉴스 목록 조회 """
def new_list_popular_day(opener, date):
    dataset = []
    for key, value in sections.items():
        html = opener.open(popular_day_url.format(value, date))
        soup = BeautifulSoup(html, 'html.parser')
        li = soup.select("ol[class='ranking_list'] > li > div >  a")
        for a in li:
            dataset.append({"date": date, "section": key, "url": a["href"], "title": a["title"]})
    return dataset


""" 댓글많은 뉴스 목록 조회 """
def new_list_popular_memo(opener, date):
    dataset = []
    for key, value in sections.items():
        html = opener.open(popular_day_url.format(value, date))
        soup = BeautifulSoup(html, 'html.parser')
        li = soup.select("ol[class='ranking_list'] > li > div >  a")
        for a in li:
            dataset.append({"date": date, "section": key, "url": a["href"], "title": a["title"]})
    return dataset


""" 날짜별로 뉴스 조회 및 저장 """
def crawel_new_date(args, news_set, opener, date):
    dirname = f"{args.output}/{date[:4]}"
    filename = f"{dirname}/{date}.csv"
    # 이미 수집된 경우는 수집하지 않음
    if os.path.isfile(filename):
        return
    # 폴더가 존재하지 않을경우 생성
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    # 뉴스 목록 조회
    news_list = []
    popular_day = new_list_popular_day(opener, date)
    news_list.extend(popular_day)
    popular_memo = new_list_popular_memo(opener, date)
    news_list.extend(popular_memo)

    # 뉴스 내용 조회
    dataset = []
    for news in news_list:
        url = news["url"]
        if url.startswith("/"):
            url = f"https://news.naver.com{url}"
        query = parse.parse_qs(parse.urlparse(url).query)
        news_id = f"{query['oid'][0]}.{query['aid'][0]}" # oid, aid로 구성된 구분자
        # 이미 조회한 경우는 제외 함
        if news_id not in news_set:
            news_set.add(news_id)
            contents = news_contents(opener, url)
            if 0 < len(contents):
                contents = "\n".join(contents)
                news["contents"] = contents
                dataset.append(news)
            # 네이버 ip 블락 방지용 sleep
            if 0 < args.sleep:
                time.sleep(args.sleep)
    # 뉴스저장
    if 0 < len(dataset):
        df = pd.DataFrame(data=dataset)
        df.to_csv(filename, sep=SEPARATOR, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=False,
                        help="뉴스를 크롤링 연도를 입력 합니다. 입력하지 않음면 오늘부터 2004년 4월 20일까지 크롤링을 합니다.")
    parser.add_argument("--output", default="naver_news", type=str, required=False,
                        help="뉴스를 저장할 폴더 입니다.")
    parser.add_argument("--sleep", default="0.25", type=float, required=False,
                        help="네이버 ip 블락 방지용 sleep")
    args = parser.parse_args()

    max_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    min_date = datetime.datetime.strptime(f"20040420", "%Y%m%d")

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

    # 뉴스를 저장할 폴더 생성
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    # 조회할 데이터 목록 생성
    dates = []
    while start_date >= end_date:
        dates.append(start_date.strftime("%Y%m%d"))
        start_date -= datetime.timedelta(1)
    
    # http request
    opener = req.build_opener()
    # crawlled news set
    news_set = set()

    with tqdm(total=len(dates), desc=f"Crawlling") as pbar:
        for i, date in enumerate(dates):
            pbar.set_postfix_str(f"date: {date}")
            crawel_new_date(args, news_set, opener, date)
            pbar.update(1)

