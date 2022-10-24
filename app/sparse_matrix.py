import os
import csv
from tqdm import tqdm
from pymongo import MongoClient


class SparseMatrix:
    def __init__(self, database, file_name):
        self.db = database['solved_ac']
        self.file_name = file_name
        self.file = open(f"{file_name}.csv", 'w', newline='', encoding='cp949')
        self.wr = csv.writer(self.file)
        self.wr.writerow(['userId', 'problemId', 'value'])

    
    def __del__(self):
        self.file.close()


    def sparse_matrix_v1(self):
        """interact가 있는 경우(시도한 이력이 있을 경우) 1, 없으면 0"""
        users = list(self.db['user'].find())
        problems = list(self.db['problem'].find({"isHotProblem": True}))

        pbar = tqdm(total=len(users)*len(problems))
        for user in users:
            for problem in problems:
                pbar.update(1)
                if self.db['interact'].find_one({
                    "$and": [
                        {"userId": user['userId']},
                        {"problemId": str(problem['problemId'])}
                    ]
                }):
                    rating = 1
                else:
                    rating = 0

                self.wr.writerow(
                    [user['userNumber'], problem['problemId'], rating]
                )
        pbar.close()
    

    def sparse_matrix_v2(self):
        """interact가 있고, 힘겹게 풀어서 맞췄을 경우(5번 이상 실패) 2, 없으면 0"""
        users = list(self.db['user'].find())
        problems = list(self.db['problem'].find({"isHotProblem": True}))

        pbar = tqdm(total=len(users)*len(problems))
        for user in users:
            for problem in problems:
                pbar.update(1)
                if self.db['interact'].find_one({
                    "$and": [
                        {"userId": user['userId']},
                        {"problemId": str(problem['problemId'])}
                    ]
                }):
                    rating = 1
                    fail = list(self.db['interact'].find({
                            "$and": [
                            {"userId": user['userId']},
                            {"problemId": str(problem['problemId'])},
                            {"result": {"$not": {"$regex": "(맞았습니다!!|컴파일 에러)"}}}
                        ]
                    }))
                    if len(fail) >= 5:
                        if self.db['interact'].find_one({
                                "$and": [
                                {"userId": user['userId']},
                                {"problemId": str(problem['problemId'])},
                                {"result": {"$regex": "맞았습니다!!"}}
                            ]
                        }):
                            rating = 2
                else:
                    rating = 0

                self.wr.writerow(
                    [user['userNumber'], problem['problemId'], rating]
                )
        pbar.close()



    
    def test(self):
        self.db['test'].insert_one({'test': True})



if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

    matrix = SparseMatrix(
        database=MongoClient(os.environ['LOCAL_DB']),
        file_name="sparse_matrix_v2"
    )

    #matrix.test()
    #matrix.sparse_matrix_v1()
    matrix.sparse_matrix_v2()