import random
import requests
from bs4 import BeautifulSoup
from time import time, sleep
from pymongo import MongoClient


class Crawler:
    def __init__(self, url, headers, database, down, top):
        self.url = url
        self.headers = headers
        self.db = database
        self.down = down
        self.top = top


    def get_problem(self):
        for data in self.db['solved_ac']['problem'].find():
            url = f"https://www.acmicpc.net/problem/{data['problemId']}"
            sleep(random.uniform(1, 3))
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")

            #문제 정보
            information = soup.select('#problem-info td')
            info = []
            for io in information:
                info.append(io.text)
            #문제 설명
            description = soup.select_one('#problem_description > p').text
            #입력
            input = soup.select_one('#problem_input > p').text
            #출력
            output = soup.select_one('#problem_output').text
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


            
    
"""
백준 문제 url: https://www.acmicpc.net/problem/1000
백준 특정 문제 통계 url: https://www.acmicpc.net/problem/status/1000
백준 전체 통계 url: https://www.acmicpc.net/status?problem_id=1264


문제 채점현황 맨 마지막 url: https://www.acmicpc.net/status?problem_id=1845&from_problem=1&top=16738296
다음 페이지가 없으므로 다음 페이지 없는걸로 크롤링 종료를 할 수 있음.

각 문제별로 어디까지 수집했는지 


"""



if __name__ == '__main__':
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    crawler = Crawler(
        url="https://solved.ac/api/v3/search/problem?query=solvable:true+tier:{}&page={}",
        headers=headers,
        database=MongoClient("mongodb://localhost:27017/"),
        down=1, 
        top=10
    )

    crawler.get_problem()