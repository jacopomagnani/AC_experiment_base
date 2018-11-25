from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random
import numpy



author = 'Jacopo Magnani'

doc = """
Matching Game with noisy signals
"""


class Constants(BaseConstants):
    name_in_url = 'game'
    players_per_group = 2
    num_rounds = 2#60
    game_space = [0, 1]
    game_labels = ["A", "B"]
    game_sequence = [0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0,
                     1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0]
    type_space = [1, 2, 3]
    type_labels = ["X", "Y", "Z"]
    A_match_value = [160, 80, 40]
    A_reservation_value = [100, 75, 25]
    B_match_value = [160, 80, 40]
    B_reservation_value = [80, 75, 25]
    signal_space = [1, 2, 3]
    signal_names = ["red", "yellow", "blue"]
    pL = [0, 1/2, 1/2]
    pM = [0, 1, 0]
    pH = [1/2, 1/2, 0]


class Subsession(BaseSubsession):

    game = models.IntegerField()
    game_name = models.StringField()

    def creating_session(self):
        # set paying round and game sequence
        if self.round_number == 1:
            paying_round = random.randint(1, Constants.num_rounds)
            self.session.vars['paying_round'] = paying_round
            for t in range(1, Constants.num_rounds+1):
                self.in_round(t).game = Constants.game_sequence[t-1]
                self.in_round(t).game_name = Constants.game_labels[self.in_round(t).game]
        # form groups
        group_matrix = []
        players = self.get_players()
        ppg = self.session.config['players_per_group']
        for i in range(0, len(players), ppg):
            group_matrix.append(players[i:i + ppg])
        self.set_group_matrix(group_matrix)

    def initialize_group(self):
        for g in self.get_groups():
            # assign types
            for p in g.get_players():
                p.type = random.choice(Constants.type_space)
            # form random pairs
            num_players_in_group = len(g.get_players())
            id_list = list(range(1,num_players_in_group+1))
            while id_list:
                idx1 = random.randrange(0, len(id_list))
                p1 = id_list.pop(idx1)
                idx2 = random.randrange(0, len(id_list))
                p2 = id_list.pop(idx2)
                for p in self.get_players():
                    if p.id_in_group == p1:
                        p.partner_id = p2
                    elif p.id_in_group == p2:
                        p.partner_id = p1
            #  generate signals
            for p in g.get_players():
                for q in g.get_players():
                    if p.partner_id == q.id_in_group:
                        p.partner_type = q.type
                        if q.type == 1:
                            p.signal = numpy.random.choice(Constants.signal_space, p=Constants.pH)
                        elif q.type == 2:
                            p.signal = numpy.random.choice(Constants.signal_space, p=Constants.pM)
                        elif q.type == 3:
                            p.signal = numpy.random.choice(Constants.signal_space, p=Constants.pL)

    def get_outcome(self):
        for g in self.get_groups():
            if self.game == 0:
                match_value = Constants.A_match_value
                reservation_value = Constants.A_reservation_value
            elif self.game == 1:
                match_value = Constants.B_match_value
                reservation_value = Constants.B_reservation_value
            for p in g.get_players():
                for q in g.get_players():
                    if p.partner_id == q.id_in_group:
                        p.partner_choice = q.choice
                p.match = p.choice * p.partner_choice
                p.points = p.match * match_value[p.partner_type-1] + (1 - p.match) * reservation_value[p.type-1]
                if self.round_number == self.session.vars['paying_round']:
                    p.payoff = p.points
                    p.participant.vars['part1_payoff'] = p.points
                else:
                    p.payoff = c(0)

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    type = models.IntegerField()
    partner_id = models.IntegerField()
    partner_type = models.IntegerField()
    signal = models.IntegerField()
    choice = models.IntegerField(
        choices=[
            [1, 'Yes'],
            [0, 'No'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )
    partner_choice = models.IntegerField()
    match = models.IntegerField()
    late = models.IntegerField()
    points = models.IntegerField()