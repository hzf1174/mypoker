from pypokerengine.engine.card import Card
from pypokerengine.engine.player import Player
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils import card_utils
import random as rand
import pprint

class RandomPlayer(BasePokerPlayer):

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
    real_hole_card = []
    real_community_card = []

    for card in hole_card:
      real_card = Card.from_str(card)
      real_hole_card.append(real_card)

    for card in round_state["community_card"]:
      real_card = Card.from_str(card)
      real_community_card.append(real_card)

    win_rate = card_utils.estimate_hole_card_win_rate(1000, 2, real_hole_card, real_community_card)

    histories = round_state["action_histories"]

    cost = 0
    for turn in histories:
      for action in histories[turn]:
        if action["uuid"] == self.uuid:
          cost += action["amount"]

    pot = round_state["pot"]["main"]["amount"];

    raise_payoff = (pot-cost*2+20) * win_rate - (pot-cost*2+20) * (1-win_rate);
    call_payoff = (pot-cost*2) * win_rate - (pot-cost*2) * (1-win_rate);
    fold_payoff = -1 * cost * 0.5;

    if len(valid_actions) == 3:
      if raise_payoff >= call_payoff:
        if fold_payoff > raise_payoff:
          call_action_info = valid_actions[0]
        else:
          call_action_info = valid_actions[2]
      elif call_payoff >= fold_payoff:
        call_action_info = valid_actions[1]
      else:
        call_action_info = valid_actions[0]
    elif call_payoff >= fold_payoff:
      call_action_info = valid_actions[1]
    else:
      call_action_info = valid_actions[0]

    action = call_action_info["action"]
    return action  # action returned here is sent to the poker engine

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass

def setup_ai():
  return RandomPlayer()
