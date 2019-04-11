from pypokerengine.utils import card_utils
import json

win_rate_first = [0.405, 0.475, 0.53, 0.59]
jsObj = json.dumps(win_rate_first)
fileObject = open('PreflopRate.json', 'w')
fileObject.write(jsObj)
fileObject.close()
'''
win_rate_first = [0.405, 0.475, 0.53, 0.59]
with open('FlopRate.json', 'r') as f:
    win_rate_second = json.load(f)
with open('TurnRate.json', 'r') as f:
    win_rate_third = json.load(f)

win_rate_list = []
for i in range (5):
    win_rate_list.append([])
    for j in range (5):
        win_rate_list[i].append([])
        for w in range (5):
            win_rate_list[i][j].append([])

# change the number below
for i in range(5000):
    hole_cards = card_utils._pick_unused_card(2, [])
    win_first = card_utils.estimate_hole_card_win_rate(1000, 2, hole_cards)

    preflop = 4
    for j in range(0, 4):
        if win_rate_first[j] > win_first:
            preflop = j
            break

    flop_cards = card_utils._pick_unused_card(3, hole_cards)
    win_second = card_utils.estimate_hole_card_win_rate(1000, 2, hole_cards, flop_cards)

    flop = 4
    for j in range(0, 4):
        if win_rate_second[preflop][j] > win_second:
            flop = j
            break

    used = hole_cards + flop_cards
    turn_card = card_utils._pick_unused_card(1, used)

    win_third = card_utils.estimate_hole_card_win_rate(1000, 2, hole_cards, flop_cards + turn_card)

    turn = 4
    for j in range(0, 4):
        if win_rate_third[preflop][flop][j] > win_third:
            turn = j
            break

    used += turn_card
    river_card = card_utils._pick_unused_card(1, used)
    win_fourth = card_utils.estimate_hole_card_win_rate(1000, 2, hole_cards, flop_cards + turn_card + river_card)

    win_rate_list[preflop][flop][turn].append(win_fourth)

    print win_first, win_second, win_third, win_fourth, preflop, flop, turn,  i, win_rate_list


jsObj = json.dumps(win_rate_list)
fileObject = open('experience.json', 'w')
fileObject.write(jsObj)
fileObject.close()
'''