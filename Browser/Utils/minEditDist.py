import sys

def minEditDist(query,index):
    print(query)
    result = list()
    minDistBound = 5
    correct = 0
    for q in query.split(' '):
        temp_min = sys.maxsize
        temp_word = ''
        temp_correct = 0
        for key, value in index.items():
            s1 = q
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
            if(distances[-1] == 0):
                temp_min = distances[-1]
                temp_word = key
                print('distance=0:{}'.format(temp_word))
                temp_correct = 0
                break
            elif(distances[-1] < temp_min and distances[-1] > 0 and distances[-1] < minDistBound):
                temp_min = distances[-1]
                temp_word = key
                print('distance>0:{}'.format(temp_word))
                temp_correct = 1
        if(temp_word != ''):
            result.append(temp_word)
        else:
            result.append(q)
        if(temp_min > minDistBound):
            return query, 0
        correct = temp_correct
    print(correct)
    return ' '.join(result), correct