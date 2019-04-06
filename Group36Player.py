from pypokerengine.engine.card import Card
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils import card_utils

import random as rand
import pprint

class Group36Player(BasePokerPlayer):
  CARD_STRENGTH_FIRST = {
    1: 0.405,
    2: 0.475,
    3: 0.53,
    4: 0.59
  }

  CARD_STRENGTH_OTHERS = {
    1: 0.2,
    2: 0.4,
    3: 0.6,
    4: 0.8
  }

  ACTION = {
    "CALL" : 1,
    "RAISE" : 2,
    "FOLD" : 3,
    "SMALLBLIND" : 4,
    "BIGBLIND" : 5
  }

  def __init__(self):
    self.CF_value = {}
    self.regret = {}
    self.strategy = {}
    self.sum = {}
    self.card_strength_squared = []
    self.real_hole_card = []
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

    print tuple_info

    cost = self.calculate_costs(histories)
    print cost

    if not self.CF_value.has_key(tuple_info):
      self.CF_value[tuple_info] = 0
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
    self.game_num += 1
    self.total_contribution = 1.0

  def receive_round_start_message(self, round_count, hole_card, seats):
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
      card_strength = self.calculate_card_strength(win_rate, True)
    else:
      card_strength = self.calculate_card_strength(win_rate, False)

    self.card_strength_squared.append(card_strength)

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
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

    print cost
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(histories)

    if not self.sum.has_key(tuple_info):
      self.sum[tuple_info] = payoff
    else:
      self.sum[tuple_info] += payoff

    self.CF_value[tuple_info] = self.sum[tuple_info] / (self.total_contribution * self.game_num)

    is_me = round_state["seats"][round_state["next_player"]]["uuid"] != self.uuid
    last_CF_value = self.CF_value[tuple_info]

    while True:
      for i in range (5, 1, -1):
        last_action = info[i] % 4
        info[i] = (info[i] - last_action) / 4
        print info

        tuple_info = tuple(info)

        tuple_info_call = self.tuple_action(info, "call")

        info_if_call = list(info)
        info_if_call[i] = info_if_call[i] * 4 + 1
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

        if not is_me:
          self.CF_value[tuple_info] = last_CF_value
          is_me = not is_me
        else:
          self.CF_value[tuple_info] = (self.CF_value[tuple_info_if_raise] * self.strategy[tuple_info_raise] +
                                       self.CF_value[tuple_info_if_call] * self.strategy[tuple_info_call] +
                                       self.CF_value[tuple_info_if_fold] * self.strategy[tuple_info_fold])
          self.regret[tuple_info_raise] += self.CF_value[tuple_info_if_raise] - self.CF_value[tuple_info]
          self.regret[tuple_info_call] += self.CF_value[tuple_info_if_call] - self.CF_value[tuple_info]
          self.regret[tuple_info_fold] += self.CF_value[tuple_info_if_fold] - self.CF_value[tuple_info]
          if self.strategy[tuple_info_raise] == -1:
            strategies = self.regret_matching([self.regret[tuple_info_call], self.regret[tuple_info_fold]])
            self.strategy[tuple_info_call] = strategies[0]
            self.strategy[tuple_info_fold] = strategies[1]
          else:
            strategies = self.regret_matching([self.regret[tuple_info_call], self.regret[tuple_info_fold]],
                                              self.regret[tuple_info_raise])
            self.strategy[tuple_info_call] = strategies[0]
            self.strategy[tuple_info_fold] = strategies[1]
            self.strategy[tuple_info_raise] = strategies[2]
          is_me = not is_me
          last_CF_value = self.CF_value[tuple_info]
          break
        if info[2] == 0:
          break

      self.card_strength_squared = []
      self.real_hole_card = []

  def calculate_card_strength(self, win_rate, flag):
    if flag:
      for i in range(1, 5):
        if self.CARD_STRENGTH_FIRST[i] >= win_rate:
          return i
      return 5

    else:
      for i in range(1, 5):
        if self.CARD_STRENGTH_OTHERS[i] >= win_rate:
          return i
      return 5

  def calculate_costs(self, histories):
    cost = 0
    for turn in histories:
      amount = 0
      for action in histories[turn]:
        if action["uuid"] == self.uuid and action["amount"] > amount:
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
    min_regret = regrets[0]
    sum_regret = 0
    for i in range(0, len(regrets)):
      if min_regret > regrets[i]:
        min_regret = regrets
      sum_regret+= regrets[i]
    sum_regret -= len(regrets) * min_regret

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
