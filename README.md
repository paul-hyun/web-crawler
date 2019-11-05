# 웹 크롤러 (web-crawler)
딥러닝에 필요한 데이터를 인터넷에서 크롤링하기 위한 기능들을 모음 입니다.

## 환경
* Python(>=3.6)

```sh
$ pip install tqdm
$ pip install pandas
$ pip install bs4
```

## 네이버뉴스 크롤링
```sh
$ python naver_news.py [--year] [--output] [--sleep]
```

#### 주요옵션
* year: 특정년도의 뉴스를 크롤링 합니다. 입력하지 않으면 오늘부터 2004년 4월 20일까지 크롤링을 합니다.
* output: 뉴스를 저장할 폴더 입니다. 기본값은 naver_news 입니다.
* sleep: 혹시나 naver 측에서 ip를 차단 방지를 위한 sleep 입니다 (초단위). 기본값은 0.25초

#### 결과
* 연도 yyyy 폴더 아래 yyyymmdd.csv 형태로 날짜별로 저정됩니다.
* 컬럼은 [날짜/뉴스타입/url/제목/내용] 순으로 구성 되어 있습니다.
* 뉴스타입은 [정치,경제,사회,생활문화,세계,IT과학] 으로 구성 되어 있습ㄴ디ㅏ.
```
date,section,url,title,contents
20190817,정치,/main/ranking/read.nhn?...,"..."
...
```

#### 기타
* 이미 조회된 파일이 존재하는 경우는 다시 조회하지 않습니다. 다시 조회할 필요가 있을 경우는 해당 날짜의 파일을 삭제 후 실행하세요.

