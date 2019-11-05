# 웹 크롤러 (web-crawler)
딥러닝에 필요한 데이터를 인터넷에서 크롤링하기 위한 기능들을 모음 입니다.

## 환경
* Python(>=3.6)

```sh
$ pip install tqdm
$ pip install pandas
$ pip install bs4
$ pip install wget
```

## 네이버뉴스 얼론사별 클롤링
* 네이버 뉴스를 언론사별로 크롤링 하는 기능 입니다.
* 전체 목록을 크롤링 하는경우 동영상뉴스가 많은 부분을 차지하여 노이즈에 가까운 데이터가 수집되기 때문에 언론사별로 수집하도록 하였습니다.

```sh
$ python naver_news.py --oid <언론사> [--year] [--output] [--sleep]
```

#### 주요옵션
* oid: 뉴스를 수집할 언론사 입니다. khan(경향신문), kmib(국민일보), donga(동아일보), munhwa(문화일보), seoul(서울신문), segye(세계일보), chosun(조선일보), joins(중앙일보), hani(한겨레), hankook(한국일보) 하나를 입력하면 됩니다.
* year: 특정년도의 뉴스를 크롤링 합니다. 입력하지 않으면 오늘부터 2004년 4월 20일까지 크롤링을 합니다.
* output: 뉴스를 저장할 폴더 입니다. 기본값은 naver_news 입니다.
* sleep: 혹시나 naver 측에서 ip를 차단 방지를 위한 sleep 입니다 (초단위). 기본값은 0.01초

#### 결과
* 저장폴더/언론사/연도/yyyymmdd.csv 형태로 날짜별로 저정됩니다.
* 컬럼은 [url/제목/내용] 순으로 구성 되어 있습니다.
* seperator는 \u241D를 사용 하였습니다.
```
url,title,text
/main/ranking/read.nhn?...,"..."
...
```
* pandas를 이용하면 쉽게 사용할 수 있습니다.
```
SEPARATOR = u"\u241D"
df = pd.read_csv(filename, sep=SEPARATOR, engine="python")
```

#### 기타
* 이미 조회된 파일이 존재하는 경우는 다시 조회하지 않습니다. 다시 조회할 필요가 있을 경우는 해당 날짜의 파일을 삭제 후 실행하세요.




## 한국어 위키 크롤링
* 위키피디아 한국어 버전을 크롤링 하는 기능 입니다.
* 위키파싱은 [https://github.com/attardi/wikiextractor]의 WikiExtractor.py를 사용 했습니다.

```sh
$ python kowiki.py [--output]
```

#### 주요옵션
* output: 위키를 저장할 폴더 입니다. 기본값은 kowiki 입니다.

#### 결과
* 저장폴더/yyyymmdd.csv 형태로 날짜별로 저정됩니다.
* 컬럼은 [id/url/제목/내용] 순으로 구성 되어 있습니다.
* seperator는 \u241D를 사용 하였습니다.
```
id,url,title,text
5,https://ko.wikipedia.org/wiki?curid=5,"..."
...
```
* pandas를 이용하면 쉽게 사용할 수 있습니다.
```
SEPARATOR = u"\u241D"
df = pd.read_csv(filename, sep=SEPARATOR, engine="python")
```

