import os
import sys
import random
import requests
from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup
from pymongo import MongoClient


class ProblemCrawler:
    def __init__(self, headers, database):
        self.headers = headers
        self.db = database['Jarvis']

    
    def get_problem(self):
        problems = list(self.db['problem'].find())
        pbar = tqdm(total=len(problems))
        for data in problems:
            #이미 수집한 문제는 넘어감
            if 'description' in data.keys():
                pbar.update(1)
                continue
            url = f"https://www.acmicpc.net/problem/{data['problemId']}"
            sleep(random.uniform(0.5, 2))
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")

            #문제 정보
            information = soup.select('#problem-info td')
            info = []
            for io in information:
                info.append(io.text)
            #문제 설명
            description = soup.select_one('#problem_description')
            for a in description.select('a'):
                a.unwrap()
            #입력
            input = soup.select_one('#problem_input')
            for a in input.select('a'):
                a.unwrap()
            #출력
            output = soup.select_one('#problem_output')
            for a in output.select('a'):
                a.unwrap()
            #제한
            limit_parent = soup.select_one('#limit')
            if (
                limit_parent.has_attr('style') and 
                limit_parent['style'].replace(' ', '') == "display:none;"
            ):
                limit = None
            else:
                limit = soup.select_one('#problem_limit')
                for a in limit.select('a'):
                    a.unwrap()
            #노트 (힌트)
            note_parent = soup.select_one('#hint')
            if (
                note_parent.has_attr('style') and 
                note_parent['style'].replace(' ', '') == "display:none;"
            ):
                note = None
            else:
                note = soup.select_one('#problem_hint')
                for a in note.select('a'):
                    a.unwrap()
            #예제 입력, 출력
            #TODO: 예제 입력 출력은 다양하게 여러가지일 수 있으니 조사 필요
            example = []
            cnt = 1
            while True:
                sample_input = soup.select_one(f"#sample-input-{cnt}")
                sample_output = soup.select_one(f"#sample-output-{cnt}")
                sample_explain = soup.select_one(f"#problem_sample_explain_{cnt}")
                if not sample_input:
                    break
                if sample_explain:
                    for a in sample_explain.select('a'):
                        a.unwrap()
                example.append({
                    'sample_input': sample_input.text,
                    'sample_output': sample_output.text,
                    'sample_explain': str(sample_explain) if sample_explain else None
                })
                cnt += 1
                    
            result = {
                'timeLimit': float(info[0].replace(' ', '').replace('초', '')),
                'memoryLimit': int(info[1].replace(' ', '').replace('MB', '')),
                'submit': int(info[2]),
                'correct': int(info[3]),
                'correctPeople': int(info[4]),
                'correctPecent': float(info[5].replace(' ', '').replace('%', '')),
                'description': str(description),
                'input': str(input),
                'output': str(output),
                'example': example,
                'limit': str(limit) if limit else None,
                'note': str(note) if note else None
            }
            self.db['test'].insert_one(result)
            pbar.update(1)
        pbar.close()


    def test(self, problem):
        url = f"https://www.acmicpc.net/problem/{problem}"
        sleep(random.uniform(0.5, 2))
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        #문제 정보
        information = soup.select('#problem-info td')
        info = []
        for io in information:
            info.append(io.text)
        #문제 설명
        description = soup.select_one('#problem_description')
        for a in description.select('a'):
            a.unwrap()
        #입력
        input = soup.select_one('#problem_input')
        for a in input.select('a'):
            a.unwrap()
        #출력
        output = soup.select_one('#problem_output')
        for a in output.select('a'):
            a.unwrap()
        #제한
        limit_parent = soup.select_one('#limit')
        if (
            limit_parent.has_attr('style') and 
            limit_parent['style'].replace(' ', '') == "display:none;"
        ):
            limit = None
        else:
            limit = soup.select_one('#problem_limit')
            for a in limit.select('a'):
                a.unwrap()
        #노트 (힌트)
        note_parent = soup.select_one('#hint')
        if (
            note_parent.has_attr('style') and 
            note_parent['style'].replace(' ', '') == "display:none;"
        ):
            note = None
        else:
            note = soup.select_one('#problem_hint')
            for a in note.select('a'):
                a.unwrap()
        #예제 입력, 출력
        #TODO: 예제 입력 출력은 다양하게 여러가지일 수 있으니 조사 필요
        example = []
        cnt = 1
        while True:
            sample_input = soup.select_one(f"#sample-input-{cnt}")
            sample_output = soup.select_one(f"#sample-output-{cnt}")
            sample_explain = soup.select_one(f"#problem_sample_explain_{cnt}")
            if not sample_input:
                break
            if sample_explain:
                for a in sample_explain.select('a'):
                    a.unwrap()
            example.append({
                'sample_input': sample_input.text,
                'sample_output': sample_output.text,
                'sample_explain': str(sample_explain) if sample_explain else None
            })
            cnt += 1
                
        result = {
            'timeLimit': float(info[0].replace(' ', '').replace('초', '')),
            'memoryLimit': int(info[1].replace(' ', '').replace('MB', '')),
            'submit': int(info[2]),
            'correct': int(info[3]),
            'correctPeople': int(info[4]),
            'correctPecent': float(info[5].replace(' ', '').replace('%', '')),
            'description': str(description),
            'input': str(input),
            'output': str(output),
            'example': example,
            'limit': str(limit) if limit else None,
            'note': str(note) if note else None
        }
        self.db['test'].insert_one(result)



"""

백준 문제 url: https://www.acmicpc.net/problem/1000

각 설명마다, 리스트 형식으로 작성이 되어있는 경우도 있고, 그림이 삽입된 경우도 존재함.
리스트 예제: https://www.acmicpc.net/problem/11723
그림 예제: https://www.acmicpc.net/problem/23291  -> 제한이 추가됨.
총망라 예제: https://www.acmicpc.net/problem/23290  -> 노트도 존재, 예제 입력에도 그림과 설명이 존재함.

"""



if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    crawler = ProblemCrawler(
        headers=headers,
        database=MongoClient(os.environ['REAL_DB'])
    )

    crawler.test(23290)
    #crawler.get_problem()