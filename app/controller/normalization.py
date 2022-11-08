import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler


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


def robust_scaling(value):
    """
    Robust Scaler
    """
    print(value)
    value = [[v] for v in value]
    transformer = RobustScaler()
    transformer.fit(value)
    result = transformer.transform(value)
    return [v[0] for v in result]


def standard_scaling(value):
    """
    Standard Scaler
    """
    value = [[v] for v in value]
    transformer = StandardScaler()
    transformer.fit(value)
    result = transformer.transform(value)
    return [v[0] for v in result]


def custom_scaling_v1(value):
    """
    (value * 2) / 최대값
    """
    _max = max(value)
    data = []
    for v in value:
        data.append((v*2)/_max)
    return data


def custom_scaling_v2(value, target):
    """
    value / target
    """
    data = []
    for v in value:
        if v > 10:
            v = 10
        data.append(v/target)
    return data


if __name__ == '__main__':
    data = [1,2,6,4,7,4,1,90]
    # print("max_normalize")
    # result = max_normalize(data, 10)
    # print(result)
    # print("min_max_scaling")
    # result = min_max_scaling(data, 5)
    # print(result)
    # print("robust_scaling")
    # result = standard_scaling(data)
    # print(result)



