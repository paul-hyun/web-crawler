import os, argparse, datetime, time, re, wget, json
from tqdm import tqdm, trange
import pandas as pd


SEPARATOR = u"\u241D"


""" wiki file 목록을 읽어들임 """
def list_wiki(dirname):
    filepaths = []
    filenames = os.listdir(dirname)
    for filename in filenames:
        filepath = os.path.join(dirname, filename)

        if os.path.isdir(filepath):
            filepaths.extend(list_wiki(filepath))
        else:
            find = re.findall(r"wiki_[0-9][0-9]", filepath)
            if 0 < len(find):
                filepaths.append(filepath)
    return sorted(filepaths)


""" 여러줄띄기(\n\n...) 한줄띄기로(\n) 변경 """
def trim_text(line):
    data = json.loads(line)
    text = data["text"]
    value = list(filter(lambda x: len(x) > 0, text.split('\n')))
    data["text"] = "\n".join(value)
    return data


""" csv 파일을 제외한 나머지 파일 삭제 """
def del_garbage(dirname):
    filenames = os.listdir(dirname)
    for filename in filenames:
        filepath = os.path.join(dirname, filename)

        if os.path.isdir(filepath):
            del_garbage(filepath)
            os.rmdir(filepath)
        else:
            if not filename.endswith(".csv"):
                os.remove(filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="kowiki", type=str, required=False,
                        help="위키를 저장할 폴더 입니다.")
    args = parser.parse_args()

    # wiki를 저장할 폴더 생성
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    filename = wget.download("https://dumps.wikimedia.org/kowiki/latest/kowiki-latest-pages-meta-current.xml.bz2", args.output)
    os.system(f"python WikiExtractor.py -o {args.output} --json {filename}")

    # text 여러줄 띄기를 한줄 띄기로 합침
    dataset = []
    filenames = list_wiki(args.output)
    for filename in filenames:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    dataset.append(trim_text(line))
    
    # 자장파일 결정
    now = datetime.datetime.now().strftime("%Y%m%d")
    output = f"{args.output}/kowiki_{now}.csv"

    # 위키저장 (csv)
    if 0 < len(dataset):
        df = pd.DataFrame(data=dataset)
        df.to_csv(output, sep=SEPARATOR, index=False)
    
    # 파일삭제
    del_garbage(args.output)
