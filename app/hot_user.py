import os
import numpy as np
from pymongo import MongoClient
from matplotlib import pyplot as plt
from matplotlib import ticker as ticker


def get_hot_user(database: MongoClient):
    db = database['Jarvis']
    col = db['interact']
    users = col.distinct('userId')
    #전체 유저 수
    print(len(users))

    interact = list(col.aggregate([
        {
            "$group": {
                "_id": "$userId",
                "count": {"$sum": 1}
            }
        }
    ]))

    avg = list(col.aggregate([
        {
            "$group": {
                "_id": "$userId",
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {
                "count": {"$gt": 400}
            }
        }
    ]))
    avg = sorted(avg, key=lambda x: x['count'])


    graph = sorted(x['count'] for x in interact)
    plt.figure(figsize=(25, 10))
    plt.plot(graph)
    plt.xticks(np.arange(0, 100000, step=5000))
    plt.yticks(np.arange(0, 10000, step=200))
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

    get_hot_user(
        database=MongoClient(os.environ['REAL_DB'])
    )