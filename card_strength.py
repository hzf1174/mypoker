from pypokerengine.utils import card_utils
from pypokerengine.engine.card import Card
import random
import json
import pprint
'''

win_rate_third = []
for i in range (5):
    win_rate_third.append([])
    for j in range (5):
        win_rate_third[i].append([])
        for w in range(5):
            win_rate_third[i][j].append([])
            for k in range(4):
                win_rate_third[i][j][w].append([])


for i in range(0, 5):
    for j in range(0, 5):
        for w in range(0, 5):
            list_final[i][j][w].sort()
#pp.pprint(list_third)

for i in range(0, 5):
    print "+++++++++++++++++++++++++"
    for j in range(0, 5):
        print "~~~~~~~~~~~~~"
        for w in range(0, 5):
            print "-----"
            print len(list_final[i][j][w])
            for k in range(1, 5):
                win_rate_third[i][j][w][k - 1] = list_final[i][j][w][len(list_final[i][j][w]) /5 * k]
                print win_rate_third[i][j][w][k - 1]


jsObj = json.dumps(win_rate_third)
fileObject = open('RiverRate.json', 'w')
fileObject.write(jsObj)
fileObject.close()

'''
'''
card1 = Card(2, 2)
card2 = Card(2, 6)
for rank3 in Card.RANK_MAP:
    for rank4 in Card.RANK_MAP:
        for rank5 in Card.RANK_MAP:
            for suit3 in Card.SUIT_MAP:
                for suit4 in Card.SUIT_MAP:
                    for suit5 in Card.SUIT_MAP:
                        card3 = Card(suit3, rank3)
                        card4 = Card(suit4, rank4)
                        card5 = Card(suit5, rank5)
                        cards = [card1, card2, card3, card4, card5]
                        if card1 != card3 and card1 != card4 and card1 != card5 and card2 != card3 and card2 != card4 and card2 != card5 and card3 != card4 and card3 != card5 and card4 != card5:
                            cards = [card1, card2]
                            community = [card3, card4, card5]
                            win_rate = card_utils.estimate_hole_card_win_rate(100, 2, cards, community)
                            win_rate_list.append(win_rate)
                            print(2, 2, 2, 6, card3.rank)
win_rate_list.sort()
size = len(win_rate_list)
print(win_rate_list)
print(size)
for i in range(0, 10):
    print(win_rate_list[size/10*i])
    '''
with open('experience.json', 'r') as f:
    list_final = json.load(f)

diction = {
    (1, 3, 5, "strong") : 1,
    (2, 5, 7) : 2
}

str_diction = {}
new_diction = {}

for item in diction:
    str_diction[item.__str__()] = diction[item]

for item in str_diction:
    new_diction[tuple(eval(item))] = str_diction[item]

print new_diction
