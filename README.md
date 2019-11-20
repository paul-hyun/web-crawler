# 웹 크롤러 (web-crawler)
딥러닝에 필요한 데이터를 인터넷에서 크롤링하기 위한 기능들을 모음 입니다.

## 환경
* Python(>=3.6)

```sh
$ pip install tqdm
$ pip install pandas
$ pip install bs4
$ pip install wget
$ pip install pymongo
```

## 네이버뉴스 클롤링 (CSV)
* 네이버 뉴스를 크롤링 해서 CSV 파일 형식으로 저장 기능 입니다.

```sh
$ python naver_news_csv.py [--year] [--output] [--threads] [--sleep]
```

#### 주요옵션
* year: 특정년도의 뉴스를 크롤링 합니다. 입력하지 않으면 오늘부터 2004년 4월 20일까지 크롤링을 합니다.
* output: 뉴스를 저장할 폴더 입니다. 기본값은 naver_news 입니다.
* threads: 뉴스를 수집할 쓰레스 개수 입니다. 기본값은 3 입니다.
* sleep: web request 완료 후 sleep 입니다 (초단위). 기본값은 0.01초


#### 결과
* 진행중 상태는 각 thread 별로 {thread_id: date(complete/total)} 형태로 표현 됩니다.
* {'0': '20191112(    0/ 2047)', '1': '20191111(    0/ 2144)', '2': '20191018(    0/ 2100)'}
* 저장폴더/연도/yyyymmdd.csv 형태로 날짜별로 저정됩니다.
* 컬럼은 [url/제목/내용] 순으로 구성 되어 있습니다.
* seperator는 \u241D를 사용 하였습니다.
```
url,title,text
/main/ranking/read.nhn?...,"..."
...
```
* pandas를 이용하면 쉽게 사용할 수 있습니다.
```
csv.field_size_limit(sys.maxsize)
SEPARATOR = u"\u241D"
df = pd.read_csv(filename, sep=SEPARATOR, engine="python")
```

#### 기타
* 이미 조회된 파일이 존재하는 경우는 다시 조회하지 않습니다. 다시 조회할 필요가 있을 경우는 해당 날짜의 파일을 삭제 후 실행하세요.




## 한국어 위키 크롤링 (CSV)
* 위키피디아 한국어 버전을 크롤링 하는 기능 입니다.
* 위키파싱은 [wikiextractor](https://github.com/attardi/wikiextractor)의 WikiExtractor.py를 사용 했습니다.

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
csv.field_size_limit(sys.maxsize)
SEPARATOR = u"\u241D"
df = pd.read_csv(filename, sep=SEPARATOR, engine="python")
```


## STACKOVEFLOW (CSV)
* stackoverflow 데이터를 크롤링 해서 CSV 파일 형식으로 저장 기능 입니다.

```sh
$ python stackoverflow.py [--output] [--tag] [--sleep]
```

#### 주요옵션
* output: 크로링 데이터를 저장할 폴더 입니다. 기본값은 stackoverflow 입니다.
* tag: 크롤링 할 stackoverflow tag 입니다. 기본값은 deep-learning 입니다.
* sleep: web request 완료 후 sleep 입니다 (초단위). 기본값은 0.01초


#### 결과
* 저장폴더/tag.csv 형태로 저정됩니다.
* 컬럼은 [votes/answer/title/url/overview/tags/act_time/user_img/user_id/user_home] 순으로 구성 되어 있습니다.
* seperator는 \u241D를 사용 하였습니다.
```
votes/answer/title/url/overview/tags/act_time/user_img/user_id/user_home
...
```
* pandas를 이용하면 쉽게 사용할 수 있습니다.
```
csv.field_size_limit(sys.maxsize)
SEPARATOR = u"\u241D"
df = pd.read_csv(filename, sep=SEPARATOR, engine="python")
```

