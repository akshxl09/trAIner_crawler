import json
import math
import random
import requests
from time import time, sleep
from pymongo import MongoClient


class Crawler:
    def __init__(self, url, headers, database, down, top):
        self.url = url
        self.headers = headers
        self.db = database['solved_ac']
        self.pages = self.get_page(down, top)
        self.down = down
        self.top = top


    def get_page(self, down, top):
        """최대 몇 페이지인지 반환"""
        pages = {}
        real_data = []
        for i in range(down, top+1):
            sleep(random.uniform(2, 5))
            response = requests.get(self.url.format(i, 1), headers=self.headers)
            data = json.loads(response.text)
            pages[i] = math.ceil(data['count'] / 50)    #한 페이지는 50개가 최대.
            real_data.append({
                'tier': i,
                'count': data['count'],
                'page': pages[i]
            })
            print('tier {} master_config 수집중...'.format(i))
        if real_data:
            self.db['master_config'].insert_many(real_data)
        return pages


    def get_data(self):
        #tier별로 반복
        for i in range(self.down, self.top+1):
            #page만큼 반복
            for j in range(1, self.pages[i]+1):
                sleep(random.uniform(2, 5))
                response = requests.get(self.url.format(i,j), headers=self.headers)
                data = json.loads(response.text)
                #데이터 그대로 db에 박으면 될듯?
                real_data = []
                for result in data['items']:
                    #통과한 사람 수가 100명 이상일 때만 수집
                    if result['acceptedUserCount'] >= 100:
                        real_data.append(result)
                if real_data:
                    self.db[f'tier_{i}'].insert_many(real_data)
                print('tier {}의 {} 페이지 수집중...'.format(i,j))
                

if __name__ == "__main__":
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

    process_time = time()
    crawler.get_data()
    process_time = time() - process_time
    print(process_time)