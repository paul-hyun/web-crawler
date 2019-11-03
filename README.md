# web-crawler
딥러닝에 필요한 데이터를 인터네에서 크롤링하기 위해 필요한 기능 입니다.

## 환경
- python 3.6
- pip install tqdm
- pip install pandas
- pip install bs4

## 네이버뉴스 크롤링
python naver_news.py

### 주요옵션
- year: 특정년도의 뉴스를 크롤링 합니다. 입력하지 않음면 오늘부터 2004년 4월 20일까지 크롤링을 합니다.
- output: 뉴스를 저장할 폴더 입니다. 기본값은 naver_news 입니다.
- sleep: 혹시나 naver 측에서 ip 블럭을 당할까봐 준 sleep 입니다 (초단위). 기본값은 0.25초

### 결과
- 날짜단위의 yyyymmdd.csv 형태로 저정됩니다.
- 컬럼은 [date,section,url,title,contents] 날짜/구분(정치,경제,사회,생활문화,세계,IT과학)/url/제목/내용 순으로 구성 되어 있습니다.

### 기타
- 이미 조회된 파일이 존재하는 경우는 다시 조회하지 않습니다. 다시 조회할 필요가 있을 경우는 해당 파일을 삭제 후 실행하세요.

