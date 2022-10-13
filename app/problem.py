import os
import random
import requests
from time import sleep
from bs4 import BeautifulSoup
from pymongo import MongoClient


class Crawler:
    def __init__(self, headers, database):
        self.headers = headers
        self.db = database


    def get_problem(self):
        problems = self.db['solved_ac']['problem'].find()
        for data in problems:
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
            #입력
            input = soup.select_one('#problem_input')
            #출력
            output = soup.select_one('#problem_output')
            #예제 입력, 출력
            #TODO: 예제 입력 출력은 다양하게 여러가지일 수 있으니 조사 필요
            i = 0
            ex_input = []
            ex_output = []
            while True:
                i += 1
                ex_in = soup.select_one(f'#sample-input-{i}')
                ex_out = soup.select_one(f'#sample-output-{i}')
                if ex_in and ex_out:
                    ex_input.append(ex_in.text)
                    ex_output.append(ex_out.text)
                else:
                    break
                    
            result = {
                'timeLimit': info[0].replace(' ', ''),
                'memoryLimit': info[1],
                'submit': info[2],
                'correct': info[3],
                'correctPeople': info[4],
                'correctPecent': info[5],
                'description': description,
                'input': input,
                'output': output,
                'ex_input': ex_input,
                'ex_output': ex_output
            }
            print(f"problem {data['problemId']}")
            from pprint import pprint
            pprint(result)

    
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
        #입력
        input = soup.select_one('#problem_input')
        #출력
        output = soup.select_one('#problem_output')
        #예제 입력, 출력
        #TODO: 예제 입력 출력은 다양하게 여러가지일 수 있으니 조사 필요
        i = 0
        ex_input = []
        ex_output = []
        while True:
            i += 1
            ex_in = soup.select_one(f'#sample-input-{i}')
            ex_out = soup.select_one(f'#sample-output-{i}')
            if ex_in and ex_out:
                ex_input.append(ex_in)
                ex_output.append(ex_out)
            else:
                break
                
        result = {
            'timeLimit': info[0].replace(' ', ''),
            'memoryLimit': info[1],
            'submit': info[2],
            'correct': info[3],
            'correctPeople': info[4],
            'correctPecent': info[5],
            'description': description,
            'input': input,
            'output': output,
            'ex_input': ex_input,
            'ex_output': ex_output
        }
        from pprint import pprint
        pprint(result)
    
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
    crawler = Crawler(
        headers=headers,
        database=MongoClient(os.environ['LOCAL_DB'])
    )

    crawler.test(23290)
    #crawler.get_problem()