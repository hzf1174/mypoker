import json
'''
with open('Experience1.json', 'r') as f:
    win_rate1 = json.load(f)
with open('Experience2.json', 'r') as f:
    win_rate2 = json.load(f)

for i in range(0, 5):
    for j in range(0, 5):
        for w in range(0, 5):
            win_rate1[i][j][w] += win_rate2[i][j][w]

jsObj = json.dumps(win_rate1)
fileObject = open('Experience.json', 'w')
fileObject.write(jsObj)
fileObject.close()
'''

tup = (1,2,3,4,5)
print tuple(eval(tup.__str__()))[2]
