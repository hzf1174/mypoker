from pypokerengine.engine.card import Card
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils import card_utils

import random as rand
import pprint
import json

class Group36Player(BasePokerPlayer):
  ACTION = {
    "CALL" : 1,
    "RAISE" : 2,
    "FOLD" : 3,
    "SMALLBLIND" : 4,
    "BIGBLIND" : 5
  }

  def __init__(self):
    '''
    with open('jsonFileStrategy.json', 'r') as f:
      self.strategy = json.load(f)
    with open('jsonFileCF.json', 'r') as f:
      self.CF_value = json.load(f)
    with open('jsonFileRegret.json', 'r') as f:
      self.regret = json.load(f)
    with open('jsonFileSum.json', 'r') as f:
      self.sum = json.load(f)
        '''
    with open('PreflopRate.json', 'r') as f:
      self.CARD_STRENGTH_PREFLOP = json.load(f)
    with open('FlopRate.json', 'r') as f:
      self.CARD_STRENGTH_FLOP = json.load(f)
    with open('TurnRate.json', 'r') as f:
      self.CARD_STRENGTH_TURN = json.load(f)
    with open('RiverRate.json', 'r') as f:
      self.CARD_STRENGTH_RIVER = json.load(f)
    self.strategy = {}
    self.CF_value = {}
    self.regret = {}
    self.sum = {}
    self.times = {}
    self.card_strength_squared = []
    self.real_hole_card = []
    self.stack_history = []
    self.total_contribution = 1.0
    self.game_num = 0

  def declare_action(self, valid_actions, hole_card, round_state):
    # valid_actions format => [raise_action_pp = pprint.PrettyPrinter(indent=2)
    #pp = pprint.PrettyPrinter(indent=2)
    #print("------------ROUND_STATE(RANDOM)--------")
    #pp.pprint(round_state)
    #print("------------HOLE_CARD----------")
    #pp.pprint(hole_card)
    #print("------------VALID_ACTIONS----------")
    #pp.pprint(valid_actions)
    #print("-------------------------------")

    histories = round_state["action_histories"]

    info = self.encoded_info(round_state)

    tuple_info = tuple(info)
    tuple_info_call = self.tuple_action(info, "call")
    tuple_info_raise = self.tuple_action(info, "raise")
    tuple_info_fold = self.tuple_action(info, "fold")
    tuple_info_if_fold = list(info)
    round = round_state["street"]
    if round == "preflop":
      tuple_info_if_fold[2] = tuple_info_if_fold[2] * 4 + 3
    elif round == "flop":
      tuple_info_if_fold[3] = tuple_info_if_fold[3] * 4 + 3
    elif round == "turn":
      tuple_info_if_fold[4] = tuple_info_if_fold[4] * 4 + 3
    else:
      tuple_info_if_fold[5] = tuple_info_if_fold[5] * 4 + 3

    tuple_info_if_fold = tuple(tuple_info_if_fold)

    #print tuple_info

    cost = self.calculate_costs(histories)

    if not self.CF_value.has_key(tuple_info):
      self.CF_value[tuple_info] = 0
      self.CF_value[tuple_info_if_fold] = -cost
      self.regret[tuple_info_raise] = 0
      self.regret[tuple_info_fold] = 0
      self.regret[tuple_info_call] = 0
      if len(valid_actions) == 3:
        self.strategy[tuple_info_call] = 0.5
        self.strategy[tuple_info_raise] = 0.5
        self.strategy[tuple_info_fold] = 0
      else:
        self.strategy[tuple_info_call] = 1.0
        self.strategy[tuple_info_fold] = 0
        self.strategy[tuple_info_raise] = -1

    r = rand.random()

    p_call = self.strategy[tuple(tuple_info_call)]
    p_fold = self.strategy[tuple(tuple_info_fold)]

    if r < p_call:
      call_action_info = valid_actions[1]
      self.total_contribution *= p_call
    elif r <= p_call + p_fold:
      call_action_info = valid_actions[0]
      self.total_contribution *= p_fold
    else:
      call_action_info = valid_actions[2]
      self.total_contribution *= (1.0 - p_call - p_fold)

    action = call_action_info["action"]
    return action  # action returned here is sent to the poker engine

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    self.game_num += 1
    self.total_contribution = 1.0
    print hole_card
    for card in hole_card:
      real_card = Card.from_str(card)
      self.real_hole_card.append(real_card)

  def receive_street_start_message(self, street, round_state):
    real_community_card = []

    for card in round_state["community_card"]:
      real_card = Card.from_str(card)
      real_community_card.append(real_card)

    win_rate = card_utils.estimate_hole_card_win_rate(1000, 2, self.real_hole_card, real_community_card)
    print win_rate
    if round_state["street"] == "preflop":
      card_strength = self.calculate_card_strength(win_rate, 1)
    elif round_state["street"] == "flop":
      card_strength = self.calculate_card_strength(win_rate, 2)
    elif round_state["street"] == "turn":
      card_strength = self.calculate_card_strength(win_rate, 3)
    else:
      card_strength = self.calculate_card_strength(win_rate, 4)

    self.card_strength_squared.append(card_strength)

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    if round_state["seats"][0]["uuid"] == self.uuid:
      stack = round_state["seats"][0]["stack"]
    else:
      stack = round_state["seats"][1]["stack"]
    self.stack_history.append(stack)

    is_tied = len(winners) == 2
    is_winner = winners[0]["uuid"] == self.uuid

    histories = round_state["action_histories"]
    cost = self.calculate_costs(histories)
    info = self.encoded_info(round_state)
    tuple_info = tuple(info)

    if is_tied:
      payoff = 0
    elif is_winner:
      payoff = cost
    else:
      payoff = -cost

    #print cost

    if not self.sum.has_key(tuple_info):
      self.sum[tuple_info] = payoff
      self.times[tuple_info] = 1
    else:
      self.sum[tuple_info] += payoff
      self.times[tuple_info] += 1

    self.CF_value[tuple_info] = self.sum[tuple_info] / (self.times[tuple_info])

    last_CF_value = self.CF_value[tuple_info]
    check_list = [0, 0, 0, 0]
    for i in range(3, 6):
      if info[i] != 0:
        check_list[i - 3] = -1

    #print check_list
    print last_CF_value
    #print self.total_contribution , self.game_num
    #print info
    while info[2] != 0:
      for i in range(5, 1, -1):
        if info[i] == 0:
          continue
        last_action = info[i] % 4
        info[i] = (info[i] - last_action) / 4

        encoded_card_strength = 0
        for j in range (0, i - 1):
          encoded_card_strength = encoded_card_strength * 6 + self.card_strength_squared[j]

        info[1] = encoded_card_strength

        tuple_info = tuple(info)
        if not self.is_me(i, info[i], histories):
          self.CF_value[tuple_info] = last_CF_value
          #print last_CF_value
        else:
          tuple_info_call = self.tuple_action(info, "call")
          info_if_call = list(info)
          info_if_call[i] = info_if_call[i] * 4 + 1
          if check_list[i - 2] == -1:
            encoded_card_strength = 0
            for j in range(0, i):
              encoded_card_strength = encoded_card_strength * 6 + self.card_strength_squared[j]
            info_if_call[1] = encoded_card_strength
          tuple_info_if_call = tuple(info_if_call)
          if not self.CF_value.has_key(tuple_info_if_call):
            self.CF_value[tuple_info_if_call] = 0

          tuple_info_raise = self.tuple_action(info, "raise")
          info_if_raise = list(info)
          info_if_raise[i] = info_if_raise[i] * 4 + 2
          tuple_info_if_raise = tuple(info_if_raise)
          if not self.CF_value.has_key(tuple_info_if_raise):
            self.CF_value[tuple_info_if_raise] = 0

          tuple_info_fold = self.tuple_action(info, "fold")
          info_if_fold = list(info)
          info_if_fold[i] = info_if_fold[i] * 4 + 3
          tuple_info_if_fold = tuple(info_if_fold)
          if not self.CF_value.has_key(tuple_info_if_fold):
            self.CF_value[tuple_info_if_fold] = 0

          if self.strategy[tuple_info_raise] == -1:
            self.CF_value[tuple_info] = (self.CF_value[tuple_info_if_call] *
                                         self.strategy[tuple_info_call] +
                                         self.CF_value[tuple_info_if_fold] *
                                         self.strategy[tuple_info_fold])
            last_CF_value = self.CF_value[tuple_info]
            self.regret[tuple_info_call] += self.CF_value[tuple_info_if_call] - self.CF_value[tuple_info]
            self.regret[tuple_info_fold] += self.CF_value[tuple_info_if_fold] - self.CF_value[tuple_info]

            print self.regret[tuple_info_call], self.regret[tuple_info_fold]

            strategies = self.regret_matching([self.regret[tuple_info_call], self.regret[tuple_info_fold]])
            self.strategy[tuple_info_call] = strategies[0]
            self.strategy[tuple_info_fold] = strategies[1]
          else:
            self.CF_value[tuple_info] = (self.CF_value[tuple_info_if_raise] *
                                         self.strategy[tuple_info_raise] +
                                         self.CF_value[tuple_info_if_call] *
                                         self.strategy[tuple_info_call] +
                                         self.CF_value[tuple_info_if_fold] *
                                         self.strategy[tuple_info_fold])
            last_CF_value = self.CF_value[tuple_info]

            self.regret[tuple_info_raise] += self.CF_value[tuple_info_if_raise] - self.CF_value[tuple_info]
            self.regret[tuple_info_call] += self.CF_value[tuple_info_if_call] - self.CF_value[tuple_info]
            self.regret[tuple_info_fold] += self.CF_value[tuple_info_if_fold] - self.CF_value[tuple_info]

            print self.regret[tuple_info_raise],  self.regret[tuple_info_call], self.regret[tuple_info_fold]

            strategies = self.regret_matching([self.regret[tuple_info_call], self.regret[tuple_info_fold],
                                              self.regret[tuple_info_raise]])
            self.strategy[tuple_info_call] = strategies[0]
            self.strategy[tuple_info_fold] = strategies[1]
            self.strategy[tuple_info_raise] = strategies[2]
        if check_list[i - 2] == -1:
          check_list[i - 2] = 0
        break

    self.card_strength_squared = []
    self.real_hole_card = []
    self.learn()

  def calculate_card_strength(self, win_rate, round):
    strength = self.card_strength_squared
    if round == 1:
      for i in range(0, 4):
        if self.CARD_STRENGTH_PREFLOP[i] > win_rate:
          return i + 1
      return 5

    elif round == 2:
      for i in range(0, 4):
        if self.CARD_STRENGTH_FLOP[strength[0] - 1][i] >= win_rate:
          return i + 1
      return 5

    elif round == 3:
      for i in range(0, 4):
        if self.CARD_STRENGTH_TURN[strength[0] - 1][strength[1] - 1][i] >= win_rate:
          return i + 1
      return 5

    else:
      for i in range(0, 4):
        if self.CARD_STRENGTH_RIVER[strength[0] - 1][strength[1] - 1][strength[2] - 1][i] >= win_rate:
          return i + 1
      return 5

  def calculate_costs(self, histories):
    cost = 0
    for turn in histories:
      amount = 0
      for action in histories[turn]:
        if action["uuid"] == self.uuid and action.has_key("amount") and action["amount"] > amount:
          amount = action["amount"]
      cost+= amount

    return cost

  def encode_history(self, histories):
    encoded_histories = {
      'preflop':0,
      'flop':0,
      'turn':0,
      'river':0
    }
    encoded_history = 0
    for turn in histories:
      for action in histories[turn]:
        act = self.ACTION[action["action"]]
        if act != 4 and act != 5:
          encoded_history = encoded_history * 4 + act
      encoded_histories[turn] = encoded_history
      encoded_history = 0

    return encoded_histories

  def tuple_action(self, info, action):
    inf = list(info)
    inf.append(action)
    return tuple(inf)

  def regret_matching(self, regrets):
    strategies = []
    sum_regret = 0
    min_regret = regrets[0]
    for i in range(0, len(regrets)):
      sum_regret += regrets[i]
      if regrets[i] > min_regret:
        min_regret = regrets[i]
    sum_regret -= min_regret * len(regrets)
    if sum_regret == 0:
      if len(regrets) == 3:
        return [0.5, 0, 0.5]
      else:
        return [1.0, 0]
    for i in range(0, len(regrets)):
      strategies.append((regrets[i] - min_regret)/sum_regret)
    return strategies

  def encoded_info(self, round_state):
    encoded_card_strength = 0
    for i in range(0, len(self.card_strength_squared)):
      encoded_card_strength = encoded_card_strength * 6 + self.card_strength_squared[i]

    histories = round_state["action_histories"]

    encoded_histories = self.encode_history(histories)

    info = [round_state["big_blind_pos"], encoded_card_strength, encoded_histories["preflop"],
            encoded_histories["flop"], encoded_histories["turn"], encoded_histories["river"]]
    return info

  def is_me(self, round, encoded_history, histories):
    num = 0
    while encoded_history != 0:
      encoded_history /= 4
      num+= 1

    if round == 2:
      round_histories = histories["preflop"]
      num += 2
    elif round == 3:
      round_histories = histories["flop"]
    elif round == 4:
      round_histories = histories["turn"]
    else:
      round_histories = histories["river"]
    return round_histories[num]["uuid"] == self.uuid

  def transfer_to_str(self, dicts):
    str_dicts = {}
    for dict in dicts:
      str_dicts[dict.__str__()] = dicts[dict]
    return str_dicts

  def transfer_to_tuple(self, dicts):
    tuple_dicts = {}
    for dict in dicts:
      tuple_dicts[tuple(eval(dict))] = dicts[dict]
    return tuple_dicts

  def learn(self):
    jsObjStackHistory = json.dumps(self.stack_history)
    jsObjStrategy = json.dumps(self.transfer_to_str(self.strategy))
    jsObjCF = json.dumps(self.transfer_to_str(self.CF_value))
    jsObjRegret = json.dumps(self.transfer_to_str(self.regret))
    jsObjSum = json.dumps(self.transfer_to_str(self.sum))

    fileObjectStackHistory = open('StackHistroy.json', 'w')
    fileObjectStrategy = open('Strategy.json', 'w')
    fileObjectCF = open('CF.json', 'w')
    fileObjectRegret = open('Regret.json', 'w')
    fileObjectSum = open('Sum.json', 'w')

    fileObjectStackHistory.write(jsObjStackHistory)
    fileObjectStrategy.write(jsObjStrategy)
    fileObjectCF.write(jsObjCF)
    fileObjectRegret.write(jsObjRegret)
    fileObjectSum.write(jsObjSum)

    fileObjectStackHistory.close()
    fileObjectStrategy.close()
    fileObjectCF.close()
    fileObjectRegret.close()
    fileObjectSum.close()
