import os
import random
import requests
from tqdm import tqdm
from time import time, sleep
from bs4 import BeautifulSoup
from pymongo import MongoClient


class Crawler:
    def __init__(self, headers, local_database, prod_database, size):
        self.headers = headers
        self.local = local_database
        self.prod = prod_database
        self.size = size


    def get_status(self):
        problems = list(self.local['solved_ac']['problem'].find())
        for data in problems:
            cur = self.prod['Jarvis']['interact_config'].find_one({'problemId': data['problemId']})
            if cur:
                count = cur['count']
                url = f"https://www.acmicpc.net/status?problem_id={cur['problemId']}&top={cur['top']}"
            else:
                count = 0
                url = f"https://www.acmicpc.net/status?problem_id={data['problemId']}"
            if count < self.size:
                print(f"문제 {data['problemId']}번")
                pbar = tqdm(total=self.size)
                pbar.update(count)
                while count < self.size:
                    sleep(random.uniform(0.5, 2))
                    response = requests.get(url, headers=self.headers)
                    soup = BeautifulSoup(response.text, "html.parser")

                    #다음 url 확인
                    next = soup.select_one('#next_page', href=True)
                    if next:
                        idx = next['href'].find('top=') + 4
                        next_page_submit_id = next['href'][idx:]
                        end = False
                    else:
                        next_page_submit_id = ''
                        end = True

                    table = soup.select('#status-table tbody tr')
                    #페이지당 최대 20개의 제출기록
                    for tr in table:
                        status = []
                        tds = tr.select('td')
                        for td in tds:
                            time = td.select_one('a')
                            if time and time.has_attr("data-timestamp"):
                                status.append(time['data-timestamp'])
                            else:
                                status.append(td.text)
                        """
                        모종의 이유로 크롤링이 멈췄다가 다시 재개될 경우,
                        이전에 수집했던 부분 다음부터 수집하도록 조건 추가
                        """
                        if cur and int(cur['currentSubmitId']) <= int(status[0]):
                            continue
                        self.prod['Jarvis']['interact'].insert_one({
                            'submitId': status[0],
                            'userId': status[1],
                            'problemId': status[2],
                            'result': status[3],
                            'memory': status[4],
                            'time': status[5],
                            'language': status[6],
                            'codeLength': status[7],
                            'timestamp': status[8]
                        })
                        count += 1
                        pbar.update(1)
                        self.prod['Jarvis']['interact_config'].update_one(
                            {'problemId': data['problemId']},
                            { '$set': {
                                    'currentSubmitId': status[0],
                                    'top': next_page_submit_id,
                                    'count': count,
                                    'end': end
                                }
                            }, upsert=True
                        )
                    #다음 페이지가 존재하지 않으면 stop
                    if end:
                        break
                    url = f"https://www.acmicpc.net/status?problem_id={data['problemId']}&top={next_page_submit_id}"
            
                pbar.close()


    def get_hot_user_status(self):
        users = list(self.prod['Jarvis']['user'].find())
        total_user_cnt = len(users)
        user_cnt = 0
        for user in users:
            cur = self.prod['Jarvis']['user'].find_one({'userId': user['userId']})
            if 'top' in cur.keys():
                count = cur['count']
                end = cur['end']
                url = f"https://www.acmicpc.net/status?user_id={cur['userId']}&top={cur['top']}"
            else:
                count = 0
                end = False
                url = f"https://www.acmicpc.net/status?user_id={user['userId']}"
            
            user_cnt += 1
            print(f"전체 {total_user_cnt}명의 유저 중 {user_cnt}번 째 유저 '{user['userId']}' 수집중")
            while not end:
                sleep(random.uniform(0.5, 2))
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, "html.parser")

                #다음 url 확인
                next = soup.select_one('#next_page', href=True)
                if next:
                    idx = next['href'].find('top=') + 4
                    next_page_submit_id = next['href'][idx:]
                    end = False
                else:
                    next_page_submit_id = ''
                    end = True
                url = f"https://www.acmicpc.net/status?user_id={user['userId']}&top={next_page_submit_id}"
                table = soup.select('#status-table tbody tr')
                #페이지당 최대 20개의 제출기록
                for tr in table:
                    status = []
                    tds = tr.select('td')
                    for td in tds:
                        time = td.select_one('a')
                        if time and time.has_attr("data-timestamp"):
                            status.append(time['data-timestamp'])
                        else:
                            status.append(td.text)
                    """
                    모종의 이유로 크롤링이 멈췄다가 다시 재개될 경우,
                    이전에 수집했던 부분 다음부터 수집하도록 조건 추가
                    """
                    if 'top' in cur.keys() and int(cur['currentSubmitId']) <= int(status[0]):
                        continue
                    self.prod['Jarvis']['interact'].update_one(
                        {'submitId': status[0]},
                        { '$set': {
                                'userId': status[1],
                                'problemId': status[2],
                                'result': status[3],
                                'memory': status[4],
                                'time': status[5],
                                'language': status[6],
                                'codeLength': status[7],
                                'timestamp': status[8]
                            }
                        }
                    )
                    count += 1
                    self.prod['Jarvis']['user'].update_one(
                        {'userId': user['userId']},
                        { '$set': {
                                'currentSubmitId': status[0],
                                'top': next_page_submit_id,
                                'count': count,
                                'end': end
                            }
                        }, upsert=True
                    )


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    crawler = Crawler(
        headers=headers,
        local_database=MongoClient(os.environ['LOCAL_DB']),
        prod_database=MongoClient(os.environ['REAL_DB']),
        size=1000
    )
    #crawler.get_status()
    crawler.get_hot_user_status()




"""
백준 문제 url: https://www.acmicpc.net/problem/1000
백준 특정 문제 통계 url: https://www.acmicpc.net/problem/status/1000
백준 전체 통계 url: https://www.acmicpc.net/status?problem_id=1264

백준 젠처 통계 url: https://www.acmicpc.net/status?user_id=nmp9981&top=49749180


문제 채점현황 맨 마지막 url: https://www.acmicpc.net/status?problem_id=1845&from_problem=1&top=16738296
다음 페이지가 없으므로 다음 페이지 없는걸로 크롤링 종료를 할 수 있음.

각 문제별로 어디까지 수집했는지 

"""