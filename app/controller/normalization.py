import numpy as np


def max_normalize(value, target):
    """
    최대값을 제한하여 정규화
    """
    data = []
    for v in value:
        if v >= target:
            data.append(target)
        else:
            data.append(v)
    return data
        

def min_max_scaling(value, decimal_point):
    """
    min max scaling
    소수점 n번째 자리까지 -> decimal_point
    https://leehah0908.tistory.com/2
    """
    _max = max(value)
    _min = min(value)
    data = []
    for v in value:
        data.append(format((v-_min)/(_max-_min), f".{decimal_point}f"))
    return data


if __name__ == '__main__':
    data = [1,2,6,4,7,4,1, 90]
    result = max_normalize(data, 10)
    print(result)
    result = min_max_scaling(data, 5)
    print(result)



