import os
import csv
from tqdm import tqdm
from pymongo import MongoClient
from collections import defaultdict


class SparseMatrix:
    def __init__(self, database, file_name):
        self.db = database['solved_ac']
        self.file_name = file_name
        self.file = open(f"{file_name}.csv", 'w', newline='', encoding='cp949')
        self.wr = csv.writer(self.file)
        self.wr.writerow(['userId', 'problemId', 'value'])
        self.users = list(self.db['user'].find().sort('userNumber', 1))
        self.problems = list(self.db['problem'].find({"isHotProblem": True}).sort('problemNumber', 1))

    
    def __del__(self):
        self.file.close()


    def sparse_matrix_v1(self):
        """interact가 있는 경우(시도한 이력이 있을 경우) 1, 없으면 0"""
        users = self.users
        problems = self.problems
        user_ids = [user['userId'] for user in users]
        problem_ids = [str(problem['problemId']) for problem in problems]

        print('interact 집계중..')
        result = list(self.db['interact'].find({
            "$and": [
                {"userId": {"$in": user_ids}},
                {"problemId": {"$in": problem_ids}}
            ]
        }))
        interact = defaultdict(dict)
        for i in result:
            interact[i['userId']][i['problemId']] = 1

        pbar = tqdm(total=len(users)*len(problems))
        for user in users:
            for problem in problems:
                pbar.update(1)
                if str(problem['problemId']) in interact[user['userId']].keys():
                    rating = 1
                else:
                    rating = 0

                self.wr.writerow(
                    [user['userNumber'], problem['problemNumber'], rating]
                )
        pbar.close()
    

    def sparse_matrix_v1_1(self):
        """interact가 있는 경우(시도한 이력이 있을 경우) 5, 없으면 1"""
        users = self.users
        problems = self.problems
        user_ids = [user['userId'] for user in users]
        problem_ids = [str(problem['problemId']) for problem in problems]

        print('interact 집계중..')
        result = list(self.db['interact'].find({
            "$and": [
                {"userId": {"$in": user_ids}},
                {"problemId": {"$in": problem_ids}}
            ]
        }))
        interact = defaultdict(dict)
        for i in result:
            interact[i['userId']][i['problemId']] = 1

        pbar = tqdm(total=len(users)*len(problems))
        for user in users:
            for problem in problems:
                pbar.update(1)
                if str(problem['problemId']) in interact[user['userId']].keys():
                    rating = 5
                else:
                    rating = 1

                self.wr.writerow(
                    [user['userNumber'], problem['problemNumber'], rating]
                )
        pbar.close()
    

    def sparse_matrix_v2(self):
        """interact가 있고, 힘겹게 풀어서 맞췄을 경우(5번 이상 실패) 2, 없으면 0"""
        users = list(self.db['user'].find())
        problems = list(self.db['problem'].find({"isHotProblem": True}))
        user_ids = [user['userId'] for user in users]
        problem_ids = [str(problem['problemId']) for problem in problems]

        print('interact 집계중..')
        result = list(self.db['interact'].find({
            "$and": [
                {"userId": {"$in": user_ids}},
                {"problemId": {"$in": problem_ids}}
            ]
        }))
        interact = defaultdict(dict)
        for i in result:
            if i['problemId'] not in interact[i['userId']].keys():
                success = 0
                fail = 0
                if i['result'] not in ("맞았습니다!!","컴파일 에러"):
                    fail = 1
                elif i['result'] == "맞았습니다!!":
                    success = 1
                interact[i['userId']][i['problemId']] = {'success': success, 'fail': fail}
            else:
                if i['result'] not in ("맞았습니다!!","컴파일 에러"):
                    interact[i['userId']][i['problemId']]['fail'] += 1
                elif i['result'] == "맞았습니다!!":
                    interact[i['userId']][i['problemId']]['success'] += 1

        pbar = tqdm(total=len(users)*len(problems))
        cnt_2 = 0
        cnt_1 = 0
        cnt_0 = 0
        for user in users:
            for problem in problems:
                pbar.update(1)
                if str(problem['problemId']) in interact[user['userId']].keys():
                    if (
                        interact[user['userId']][str(problem['problemId'])]['fail'] >= 5 and
                        interact[user['userId']][str(problem['problemId'])]['success'] >= 1
                    ):
                        rating = 2
                        cnt_2 += 1
                    else:
                        rating = 1
                        cnt_1 += 1
                else:
                    rating = 0
                    cnt_0 += 1
                self.wr.writerow(
                    [user['userNumber'], problem['problemNumber'], rating]
                )
        pbar.close()
        print(cnt_2, cnt_1, cnt_0)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

    matrix = SparseMatrix(
        database=MongoClient(os.environ['LOCAL_DB']),
        file_name="sparse_matrix_v2"
    )

    #matrix.sparse_matrix_v1()
    matrix.sparse_matrix_v2()
    #matrix.sparse_matrix_v1_1()