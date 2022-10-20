import os
import numpy as np
from tqdm import tqdm
from pymongo import MongoClient
from matplotlib import pyplot as plt


class Crawler:
    def __init__(self, database):
        self.db = database['Jarvis']


    def get_problem_by_hot_users(self):
        """백준 러버가 푼 문제들의 수 구하기"""
        users = list(self.db['user'].find({},{"_id": 0, "userId": 1}))
        pro = list(self.db['problem'].find({}, {"_id":0, "problemId": 1}))
        user_lst = [x['userId'] for x in users]
        pro_lst = [str(x['problemId']) for x in pro]
        problems = list(self.db['interact'].find(
            {
                "$and": [
                    {"userId": {"$in": user_lst}},
                    {"problemId": {"$in": pro_lst}}
                ]
            }
        ).distinct("problemId"))
        print(len(problems))

    
    def get_problem_graph(self):
        """각 문제별로 몇 명의 백준 러버가 풀었는지 그래프로 표현"""
        users = list(self.db['user'].find({},{"_id": 0, "userId": 1}))
        pro = list(self.db['problem'].find({}, {"_id":0, "problemId": 1}))
        user_lst = [x['userId'] for x in users]
        pro_lst = [str(x['problemId']) for x in pro]

        result = []
        pbar = tqdm(total=len(pro_lst))
        for pro in pro_lst:
            pbar.update(1)
            problems = list(self.db['interact'].find(
                {
                    "$and": [
                        {"problemId": pro},
                        {"userId": {"$in": user_lst}}  #백준 러버의 interact
                    ]
                },
                {
                    "_id": 0,
                    "problemId": 1,
                    "userId": 1
                }
            ).distinct("userId"))
            result.append(len(problems))
        pbar.close()

        result = sorted(result)
        plt.figure(figsize=(25, 7))
        plt.plot(result)
        plt.yticks(np.arange(0, 1000, step=50))
        plt.grid(True)
        plt.show()

    
    def check_hot_problem(self):
        """hot_problem 설정"""
        users = list(self.db['user'].find({},{"_id": 0, "userId": 1}))
        pro = list(self.db['problem'].find({}, {"_id":0, "problemId": 1}))
        user_lst = [x['userId'] for x in users]
        pro_lst = [str(x['problemId']) for x in pro]

        result = []
        pbar = tqdm(total=len(pro_lst))
        for problem_id in pro_lst:
            pbar.update(1)
            problems = list(self.db['interact'].find(
                {
                    "$and": [
                        {"problemId": problem_id},
                        {"userId": {"$in": user_lst}}  #백준 러버의 interact
                    ]
                },
                {
                    "_id": 0,
                    "problemId": 1,
                    "userId": 1
                }
            ).distinct("userId"))
            if len(problems) >= 300:
                self.db['problem'].update_one(
                    {"problemId": int(problem_id)},
                    {"$set": {"isHotProblem": True}}
                )
                result.append(len(problems))
        pbar.close()

        result = sorted(result)
        plt.figure(figsize=(20, 7))
        plt.plot(result)
        plt.yticks(np.arange(0, 1000, step=50))
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

    crawler = Crawler(
        database=MongoClient(os.environ['REAL_DB'])
    )
    #crawler.get_problem_by_hot_users()
    #crawler.get_problem_by_graph()
    crawler.check_hot_problem()