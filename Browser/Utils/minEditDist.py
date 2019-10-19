import sys

def minEditDist(query,index):
    print(query)
    result = str()
    minDist = sys.maxsize
    for key, value in index.items():
        s1 = query
        s2 = key
        if len(s1) > len(s2):
            s1, s2 = s2, s1
        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        if(distances[-1] < minDist):
            result = key
            minDist = distances[-1]
    print(result)
    return result, minDist