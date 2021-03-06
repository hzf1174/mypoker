from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from Group36Player import Group36Player

#TODO:config the config as our wish
config = setup_config(max_round=100000, initial_stack=100000, small_blind_amount=10)



config.register_player(name="f1", algorithm=Group36Player())
config.register_player(name="FT2", algorithm=RaisedPlayer())


game_result = start_poker(config, verbose=1)
