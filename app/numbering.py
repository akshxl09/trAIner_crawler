import os
import csv
from tqdm import tqdm
from pymongo import MongoClient


class Number:
    def __init__(self, database):
        self.db = database['solved_ac']
    

    def update_user_number(self):
        self.db['user'].update_many(
            {}, 
            {"$inc": {"userNumber": -1}}
        )
        return
    
    def update_problem_number(self):
        pro = list(self.db['problem'].find({"isHotProblem": True}))
        print(len(pro))
        cnt = 0
        for i in pro:
            self.db['problem'].update_one(
                {"problemId": int(i['problemId'])},
                {"$set": {"problemNumber": cnt}}
            )
            cnt += 1
        return

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

    matrix = Number(
        database=MongoClient(os.environ['LOCAL_DB'])
    )

    matrix.update_problem_number()