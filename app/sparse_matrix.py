import os
import csv
from tqdm import tqdm
from pymongo import MongoClient
from matplotlib import pyplot as plt
from collections import defaultdict
from controller import max_normalize, min_max_scaling


class SparseMatrix:
    def __init__(self, database, file_name):
        self.db = database['solved_ac']
        self.file_name = file_name
        self.path = f"{os.getcwd()}".replace('/app', '')
        self.file = open(f"{self.path}/sparse_matrix/{file_name}.csv", 'w', newline='', encoding='cp949')
        self.wr = csv.writer(self.file)
        self.wr.writerow(['userId', 'problemId', 'value'])
        self.users = list(self.db['user'].find().sort('userNumber', 1))
        self.problems = list(self.db['problem'].find({"isHotProblem": True}).sort('problemNumber', 1))

    
    def __del__(self):
        self.file.close()


    def sparse_matrix_v1(self, true_score, false_score):
        """interact가 있는 경우(시도한 이력이 있을 경우) true_score, 없으면 false_score"""
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
                    rating = true_score
                else:
                    rating = false_score

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
    

    def sparse_matrix_v3(self):
        """
        바로 맞춘 애는 0
        틀린 interact 개당 rating 1씩 늘어나고, 최대 5점
        interact 없는 경우는 애초에 제외(푼 것만 csv에 넘겨줄 것)
        """
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
                if i['result'] != "맞았습니다!!":
                    fail = 1
                elif i['result'] == "맞았습니다!!":
                    success = 1
                interact[i['userId']][i['problemId']] = {'success': success, 'fail': fail}
            else:
                if i['result'] != "맞았습니다!!":
                    interact[i['userId']][i['problemId']]['fail'] += 1
                elif i['result'] == "맞았습니다!!":
                    interact[i['userId']][i['problemId']]['success'] += 1

        pbar = tqdm(total=len(users)*len(problems))
        rating_dict = defaultdict(int)
        for user in users:
            for problem in problems:
                pbar.update(1)
                if str(problem['problemId']) in interact[user['userId']].keys():
                    #바로 맞춘 경우
                    if (
                        interact[user['userId']][str(problem['problemId'])]['fail'] == 0 and
                        interact[user['userId']][str(problem['problemId'])]['success'] >= 1
                    ):
                        rating = 0
                    # #fail이 5번 이상일 경우
                    # elif interact[user['userId']][str(problem['problemId'])]['fail'] >= 5:
                    #     rating = 5
                    else:
                        rating = interact[user['userId']][str(problem['problemId'])]['fail']
                    self.wr.writerow(
                        [user['userNumber'], problem['problemNumber'], rating]
                    )
                    rating_dict[rating] += 1
        pbar.close()
        from pprint import pprint
        pprint(rating_dict)

        tmp = []
        for i in rating_dict:
            tmp.append(rating_dict[i])
        #tmp = sorted(tmp)
        plt.plot(tmp)
        plt.grid(True)
        plt.show()


    
    def sparse_matrix_v4(self):
        """
        v3에 문제 난이도별로 점수 추가(브론즈 1점, 실버 2점, 골드 3점)
        """
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
        level = {}
        for i in range(1, 16):
            if i%5 == 0:
                level[i] = i//5
            else:
                level[i] = (i//5) + 1
        for i in result:
            if i['problemId'] not in interact[i['userId']].keys():
                success = 0
                fail = 0
                if i['result'] != "맞았습니다!!":
                    fail = 1
                elif i['result'] == "맞았습니다!!":
                    success = 1
                interact[i['userId']][i['problemId']] = {'success': success, 'fail': fail}
            else:
                if i['result'] != "맞았습니다!!":
                    interact[i['userId']][i['problemId']]['fail'] += 1
                elif i['result'] == "맞았습니다!!":
                    interact[i['userId']][i['problemId']]['success'] += 1

        pbar = tqdm(total=len(users)*len(problems))
        rating_dict = defaultdict(int)
        for user in users:
            for problem in problems:
                pbar.update(1)
                if str(problem['problemId']) in interact[user['userId']].keys():
                    rating = level[problem['level']]
                    #바로 맞춘 경우
                    if (
                        interact[user['userId']][str(problem['problemId'])]['fail'] == 0 and
                        interact[user['userId']][str(problem['problemId'])]['success'] >= 1
                    ):
                        rating += 0
                    else:
                        rating += interact[user['userId']][str(problem['problemId'])]['fail']
                    self.wr.writerow(
                        [user['userNumber'], problem['problemNumber'], rating]
                    )
                    rating_dict[rating] += 1
        pbar.close()
        from pprint import pprint
        pprint(rating_dict)

    
    def sparse_matrix_v5(self, b, s, g, normalize):
        """
        바로 맞춘 유저는 0점, 실패할 때마다 rating 1씩 추가
        난이도별로 기본점수 지급 -> 브론즈: b, 실버: s, 골드: g
        + 정규화
        """
        users = list(self.db['user'].find())
        problems = list(self.db['problem'].find({"isHotProblem": True}))
        user_ids = [user['userId'] for user in users]
        problem_ids = [str(problem['problemId']) for problem in problems]
        level_map = {str(i['problemId']): i['level'] for i in problems}

        print('interact 집계중..')
        result = list(self.db['interact'].find({
            "$and": [
                {"userId": {"$in": user_ids}},
                {"problemId": {"$in": problem_ids}}
            ]
        }))
        print('interact 집계 완료')

        interact = defaultdict(dict)
        for i in result:
            if i['userId'] not in interact.keys():
                interact[i['userId']] = defaultdict(lambda: {'success': 0, 'fail': 0})
            interact[i['userId']][i['problemId']]['success'] += i['result'] == "맞았습니다!!"
            interact[i['userId']][i['problemId']]['fail'] += i['result'] != "맞았습니다!!"
            if level_map[i['problemId']] <= 5:
                interact[i['userId']][i['problemId']]['tier'] = "b"
            elif level_map[i['problemId']] <= 10:
                interact[i['userId']][i['problemId']]['tier'] = "s"
            elif level_map[i['problemId']] <= 15:
                interact[i['userId']][i['problemId']]['tier'] = "g"
            else:
                raise RuntimeError("Level Except")
        
        data = []
        level_score = {'b': b, 's': s, 'g': g}
        pbar = tqdm(total=len(users)*len(problems))
        for user in users:
            for problem in problems:
                pbar.update(1)
                if str(problem['problemId']) in interact[user['userId']].keys():
                    #난이도별 기본점수 지급
                    rating = level_score[interact[user['userId']][str(problem['problemId'])]['tier']]
                    
                    #바로 맞춘 경우
                    if (
                        interact[user['userId']][str(problem['problemId'])]['fail'] == 0 and
                        interact[user['userId']][str(problem['problemId'])]['success'] >= 1
                    ):
                        rating += 0
                    else:
                        rating += interact[user['userId']][str(problem['problemId'])]['fail']
                    data.append([user['userNumber'], problem['problemNumber'], rating])
        #정규화
        rating_lst = [x[2] for x in data]
        if normalize == "max_normalize":
            normalized_rating = max_normalize(rating_lst, 9)
        elif normalize == "min_max_scaling":
            normalized_rating = min_max_scaling(rating_lst, 6)
        else:
            raise ValueError('unknown normalization')
        
        for i, j in zip(data, normalized_rating):
            self.wr.writerow(
                [i[0], i[1], j]
            )

        pbar.close()

    
    def get_average_failure(self):
        """
        각 유저마다 평균적으로 몇 번의 실패를 겪는지 계산
        interact가 없는 경우는 제외
        """
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
                if i['result'] != "맞았습니다!!":
                    fail = 1
                elif i['result'] == "맞았습니다!!":
                    success = 1
                interact[i['userId']][i['problemId']] = {'success': success, 'fail': fail}
            else:
                if i['result'] != "맞았습니다!!":
                    interact[i['userId']][i['problemId']]['fail'] += 1
                elif i['result'] == "맞았습니다!!":
                    interact[i['userId']][i['problemId']]['success'] += 1
        len_pro = len(problems)
        avg = []
        pbar = tqdm(total=len(users)*len(problems))
        for user in users:
            failure = 0
            for problem in problems:
                pbar.update(1)
                if str(problem['problemId']) in interact[user['userId']].keys():
                    failure += interact[user['userId']][str(problem['problemId'])]['fail']
            avg.append(failure/len_pro)
        pbar.close()
        avg = sorted(avg)
        plt.plot(avg)
        plt.grid(True)
        plt.show()

    
    def get_hot_problem_tier(self):
        """
        핫 문제 티어 비율 분석
        """

        tier = {
            'bronze': [1, 2, 3, 4, 5],
            'silver': [6, 7, 8, 9, 10],
            'gold': [11, 12, 13, 14, 15]
        }
        hot_problem = list(self.db['problem'].find({"isHotProblem": True}))
        total = len(hot_problem)
        bronze = 0
        silver = 0
        gold = 0
        etc = 0
        for p in hot_problem:
            if p['level'] in tier['bronze']:
                bronze += 1
            elif p['level'] in tier['silver']:
                silver += 1
            elif p['level'] in tier['gold']:
                gold += 1
            else:
                etc += 1
        
        print(f"total: {total}, bronze: {bronze}, silver: {silver}, gold: {gold}, wrong: {etc}")
        print(f"bronze: {bronze/total*100}, silver: {silver/total*100}, gold: {gold/total*100}, wrong: {etc}")
    
    def get_average_failure_tier(self):
        """
        티어별로 평균적으로 틀리는 횟수 집계
        """

        tier = {}
        for i in range(1, 16):
            if i in (1,2,3,4,5):
                tier[i]='bronze'
            elif i in (6,7,8,9,10):
                tier[i]='silver'
            else:
                tier[i]='gold'

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
        tier_map = {}
        for i in problems:
            tier_map[str(i['problemId'])] = tier[i['level']]

        interact = defaultdict(dict)
        for i in result:
            if tier_map[i['problemId']] not in interact[i['userId']].keys():
                success = 0
                fail = 0
                if i['result'] != "맞았습니다!!":
                    fail = 1
                elif i['result'] == "맞았습니다!!":
                    success = 1
                interact[i['userId']][tier_map[i['problemId']]] = {'success': success, 'fail': fail}
            else:
                if i['result'] != "맞았습니다!!":
                    interact[i['userId']][tier_map[i['problemId']]]['fail'] += 1
                elif i['result'] == "맞았습니다!!":
                    interact[i['userId']][tier_map[i['problemId']]]['success'] += 1

        tmp = {'bronze':0, 'silver': 0, 'gold': 0}
        total_user = len(users)
        for user in users:
            for tier in ('bronze', 'silver', 'gold'):
                if tier in interact[user['userId']].keys():
                    tmp[tier] += interact[user['userId']][tier]['fail']
        
        print(f"유저들의 평균 실패 횟수: bronze: {tmp['bronze']/(total_user)}, silver: {tmp['silver']/(total_user)}, gold: {tmp['gold']/(total_user)}")


    def get_average_failure_tier_v2(self):
        users = list(self.db['user'].find())
        problems = list(self.db['problem'].find({"isHotProblem": True}))
        user_ids = [user['userId'] for user in users]
        problem_ids = [str(problem['problemId']) for problem in problems]
        level_map = {str(i['problemId']): i['level'] for i in problems}

        print('interact 집계중...')
        result = list(self.db['interact'].find({
            "$and": [
                {"userId": {"$in": user_ids}},
                {"problemId": {"$in": problem_ids}}
            ]
        }))
        print('interact 집계 완료')
        
        interact = defaultdict(lambda: {'success': 0, 'fail': 0, "users": set()})
        for i in result:
            interact[i['problemId']]['success'] += i['result'] == "맞았습니다!!"
            interact[i['problemId']]['fail'] += i['result'] != "맞았습니다!!"
            interact[i['problemId']]['users'].add(i['userId'])
            if level_map[i['problemId']] <= 5:
                interact[i['problemId']]['tier'] = "bronze"
            elif level_map[i['problemId']] <= 10:
                interact[i['problemId']]['tier'] = "silver"
            elif level_map[i['problemId']] <= 15:
                interact[i['problemId']]['tier'] = "gold"
            else:
                raise RuntimeError("Level Except")
                
        tier_dict = {}
        for t in ('bronze', 'silver', 'gold'):
            tier_dict[t] = {'sum_problem_avg': 0, 'problem_cnt': 0}
        
        for p_id in interact:
            value = interact[p_id]
            tier_dict[value['tier']]['problem_cnt'] += 1
            tier_dict[value['tier']]['sum_problem_avg'] += value['fail'] / len(value['users'])
        
        for tier in ('bronze', 'silver', 'gold'):
            print(f"{tier}: {tier_dict[tier]['sum_problem_avg']/tier_dict[tier]['problem_cnt']}")


    def get_average_failure_tier_v3(self):
        users = list(self.db['user'].find())
        problems = list(self.db['problem'].find({"isHotProblem": True}))
        user_ids = [user['userId'] for user in users]
        problem_ids = [str(problem['problemId']) for problem in problems]
        level_map = {str(i['problemId']): i['level'] for i in problems}

        print('interact 집계중...')
        interactions = list(self.db['interact'].find({
            "$and": [
                {"userId": {"$in": user_ids}},
                {"problemId": {"$in": problem_ids}}
            ]
        }))
        print("총 인터렉션 수:", len(interactions))

        inter_dict = defaultdict(lambda: {'success': 0, 'fail': 0, "users": set()})
        for i in interactions:
            inter_dict[i['problemId']]['success'] += i['result'] == "맞았습니다!!"
            inter_dict[i['problemId']]['fail'] += i['result'] != "맞았습니다!!"
            inter_dict[i['problemId']]['users'].add(i['userId'])
            if level_map[i['problemId']] <= 5:
                inter_dict[i['problemId']]['tier'] = "B"
            elif level_map[i['problemId']] <= 10:
                inter_dict[i['problemId']]['tier'] = "S"
            elif level_map[i['problemId']] <= 15:
                inter_dict[i['problemId']]['tier'] = "G"
            else:
                raise RuntimeError("Level Except")

        tier_dict = {
            'B': {'fail': 0, 'users': 0},
            'S': {'fail': 0, 'users': 0},
            'G': {'fail': 0, 'users': 0}
        }

        for problem_id in inter_dict:
            value = inter_dict[problem_id]
            tier_dict[value['tier']]['fail'] += value['fail']
            tier_dict[value['tier']]['users'] += len(value['users'])
        
        for tier in tier_dict:
            value = tier_dict[tier]
            print(f"{tier}: {value['fail'] / value['users']}")
        
        print(tier_dict)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

    matrix = SparseMatrix(
        database=MongoClient(os.environ['LOCAL_DB']),
        file_name="sparse_matrix_v12"
    )

    #matrix.sparse_matrix_v1(5, 1)
    #matrix.sparse_matrix_v3()
    matrix.sparse_matrix_v5(0.6, 1.3, 2.0, 'min_max_scaling')
    #matrix.get_average_failure()
    #matrix.get_average_failure_tier_v2()