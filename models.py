from __future__ import division

import numpy as np
import string

import otree.models
from otree.db import models
from otree import widgets
from otree.common import Currency as c, currency_range, safe_json
from otree.constants import BaseConstants
from otree.models import BaseSubsession, BaseGroup, BasePlayer

author = 'Hernán Villamizar'

doc = """
Real Effort Task - Letter Count
This is the competition part to a Tullock Contest in form of a Real Effort Task and an Investment Decision
"""


class Constants(BaseConstants):
    name_in_url = 'tullock_Income_RET'
    players_per_group = 3
    num_rounds = 8

    t = 180  # Total Time in seconds available for both solving and staying in switch
    time_in_minutes = t / 60

    tokensper_string = 1
    tokensper_string_high = 2
    eurosper_token = c(0.2)  # make sure to change it in both models.py
    secondsper_token = 10

    increase_per_string = 4

    # this is a summarized instruction to be shown under each sequence as a reminder:
    instructions_summarized = 'Tullock_Income_RET/InstructionsSum.html'

    # Taxation Treatment
    # The following variables allow to introduce a treatment of taxation and redistribution

    treatment = True
    tax_rate = 0.3
    tax_rate_percent = tax_rate * 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):

    total_investments = models.FloatField(initial=0)  # define group variable to calculate probabilities

    # determine total investments

    def set_total_investments(self):
        total_investments = sum(p.investment_amount for p in self.get_players())
        # retrieves a list of all individual incomes
        # and sums them up
        self.total_investments = total_investments

    #  calculate probabilities
    def set_probabilities(self):
        self.set_total_investments()
        # probabilities do not add to 1 if all investments are equal (because of floats)
        # this means if all investments or offers are equal
        if len(set(p.investment_amount for p in self.get_players())) == 1:
            for p in self.get_players():
                p.prob = 1 / Constants.players_per_group
        else:
            for p in self.get_players():
                p.prob = p.investment_amount / self.total_investments
        for p in self.get_players():
            p.prob_percent = p.prob * 100

    # determine winner
    def set_winner(self):
        prob = [
            p.prob for p in self.get_players()  # creates list of probabilities
            ]
        prob2 = []  # creates empty list to be normalized in next step
        for i in prob:
            prob2.append(i / sum(prob))  # this normalizes the variable and makes sure that probabilities sum up to 1
        winner = np.random.choice(self.get_players(), p=prob2)
        winner.is_winner = True
        for p in self.get_players():
            p.participant.vars['is_winner'] = p.is_winner

    # determine income:
    def set_incomes(self):  # income is defined in Tokens. What a player obtains at the end in currency are payoffs
        if Constants.treatment:  # if taxation and redistribution are implemented. Only work income is taxed.
            for p in self.get_players():
                if self.round_number > 1:
                    if p.in_round(self.round_number - 1).is_winner:
                        p.income_strings_gross = p.production_strings * Constants.tokensper_string_high
                        p.income_strings_after_tax = p.income_strings_gross * (1 - Constants.tax_rate)
                    else:
                        p.income_strings_gross = p.production_strings * Constants.tokensper_string
                        p.income_strings_after_tax = p.income_strings_gross * (1 - Constants.tax_rate)

                else:   # in the first round all start equally
                    p.income_strings_gross = p.production_strings * Constants.tokensper_string
                    p.income_strings_after_tax = p.income_strings_gross * (1 - Constants.tax_rate)

        else:   # if taxation and redistribution are NOT implemented
            for p in self.get_players():
                if self.round_number > 1:
                    if p.in_round(self.round_number - 1).is_winner:
                        p.income_strings_gross = p.production_strings * Constants.tokensper_string_high
                        p.income_strings_after_tax = p.income_strings_gross
                    else:
                        p.income_strings_gross = p.production_strings * Constants.tokensper_string
                        p.income_strings_after_tax = p.income_strings_gross
                else:   # in the first round all start equally
                    p.income_strings_gross = p.production_strings * Constants.tokensper_string
                    p.income_strings_after_tax = p.income_strings_gross


    # determine redistribution

    total_fiscal = models.FloatField(initial=0)
    transfer = models.FloatField(initial=0)  # the amount per round that each participant receives

    def set_fiscal(self):
        if Constants.treatment:  # if taxation and redistribution are implemented
            # define sum to be redistributed:
            for p in self.get_players():
                p.taxation = p.income_strings_gross * Constants.tax_rate
            total_fiscal = sum(p.taxation for p in self.get_players())

            self.total_fiscal = total_fiscal

            # Redistribute total Budget equally among participants
            for p in self.get_players():
                self.transfer = self.total_fiscal/Constants.players_per_group
                p.available_income = self.transfer + p.income_strings_after_tax
                p.net_income = p.income_strings_after_tax + p.income_in_switch + self.transfer

        else:  # if taxation and redistribution are NOT implemented
            for p in self.get_players():
                p.available_income = p.income_strings_gross
                p.net_income = p.income_strings_gross + p.income_in_switch

    # determine payoffs:
    def set_payoffs(self):
        for p in self.get_players():
            p.earnings = p.net_income - p.investment_amount
            p.payoff = p.earnings * Constants.eurosper_token


class Player(BasePlayer):

    # give each player a letter for identification (Important for Feedback)
    def role(self):
        return string.ascii_uppercase[self.id_in_group - 1]

    # Beliefs Variables

    investment_belief_0 = models.FloatField()
    investment_belief_1 = models.FloatField()

    production_belief_0 = models.PositiveIntegerField()
    production_belief_1 = models.PositiveIntegerField()

    # Contest Variables
    is_winner = models.BooleanField(
        initial=False,
        doc="""Indicates whether the player is the winner of the Tullock Contest"""
    )

    prob = models.FloatField(
        doc="Probabilities of getting the Prize in the next round. Tullock"
    )

    prob_percent = models.FloatField(
        doc="Probabilities in percent of getting the prize in next round. Tullock"
    )
    investment_amount = models.FloatField(
        default=0,
        doc="Amount bidden by the player"
    )

    # Real Effort Task variables
    # Number of Tasks Solved
    production_strings = models.FloatField(default=0)
    income_in_switch = models.FloatField(default=0)
    total_production = models.FloatField(default=0)  # the sum in tokens of earnings from string solving (gross) and switch

    # available income after solving RET
    income_strings_gross = models.FloatField(default=0)
    income_strings_after_tax = models.FloatField(default=0)
    income_after_redistribution = models.FloatField(default=0)
    net_income = models.FloatField(default=0)
    available_income = models.FloatField(default=0)  # what players are allowed to invest
    earnings = models.FloatField(default=0)  # what players keep after redistribution *and* investment
    taxation = models.FloatField(default=0)  # amount taxed for given participant

    # Variable is 1 when entering switch
    switch1 = models.PositiveIntegerField(default=0)  # word "switch" cannot be used as a variable in javascript

    switch_time = models.PositiveIntegerField(default=0)

    time_in_switch = models.PositiveIntegerField(default=0)

    additional_time = models.PositiveIntegerField(default=0)

    # correct to allow a variable number of tasks
    # for now, created with:
    # for i in range(10, 46):
    # print('t1{} = models.PositiveIntegerField(default=0)'.format(i))

    # def set_time_fields(self):
    #     for i in range(31):
    #         self.participant.vars['t1{}'.format(i)] = models.PositiveIntegerField(default=0)
    #     print(self.participant.vars)

    # Time Needed to Solve Task i in Round j with tjxi
    t101 = models.PositiveIntegerField(default=0)
    t102 = models.PositiveIntegerField(default=0)
    t103 = models.PositiveIntegerField(default=0)
    t104 = models.PositiveIntegerField(default=0)
    t105 = models.PositiveIntegerField(default=0)
    t106 = models.PositiveIntegerField(default=0)
    t107 = models.PositiveIntegerField(default=0)
    t108 = models.PositiveIntegerField(default=0)
    t109 = models.PositiveIntegerField(default=0)
    t110 = models.PositiveIntegerField(default=0)
    t111 = models.PositiveIntegerField(default=0)
    t112 = models.PositiveIntegerField(default=0)
    t113 = models.PositiveIntegerField(default=0)
    t114 = models.PositiveIntegerField(default=0)
    t115 = models.PositiveIntegerField(default=0)
    t116 = models.PositiveIntegerField(default=0)
    t117 = models.PositiveIntegerField(default=0)
    t118 = models.PositiveIntegerField(default=0)
    t119 = models.PositiveIntegerField(default=0)
    t120 = models.PositiveIntegerField(default=0)
    t121 = models.PositiveIntegerField(default=0)
    t122 = models.PositiveIntegerField(default=0)
    t123 = models.PositiveIntegerField(default=0)
    t124 = models.PositiveIntegerField(default=0)
    t125 = models.PositiveIntegerField(default=0)
    t126 = models.PositiveIntegerField(default=0)
    t127 = models.PositiveIntegerField(default=0)
    t128 = models.PositiveIntegerField(default=0)
    t129 = models.PositiveIntegerField(default=0)
    t130 = models.PositiveIntegerField(default=0)
    t131 = models.PositiveIntegerField(default=0)
    t132 = models.PositiveIntegerField(default=0)
    t133 = models.PositiveIntegerField(default=0)
    t134 = models.PositiveIntegerField(default=0)
    t135 = models.PositiveIntegerField(default=0)
    t136 = models.PositiveIntegerField(default=0)
    t137 = models.PositiveIntegerField(default=0)
    t138 = models.PositiveIntegerField(default=0)
    t139 = models.PositiveIntegerField(default=0)
    t140 = models.PositiveIntegerField(default=0)
    t141 = models.PositiveIntegerField(default=0)
    t142 = models.PositiveIntegerField(default=0)
    t143 = models.PositiveIntegerField(default=0)
    t144 = models.PositiveIntegerField(default=0)
    t145 = models.PositiveIntegerField(default=0)

    def set_switch(self):
        # Time at which switch was entered
        self.switch_time = self.switch1 * (
            self.additional_time + self.t101 + self.t102 + self.t103 + self.t104 + self.t105 +
            self.t106 + self.t107 + self.t108 + self.t109 + self.t110 +
            self.t111 +
            self.t112 +
            self.t113 +
            self.t114 +
            self.t115 +
            self.t116 +
            self.t117 +
            self.t118 +
            self.t119 +
            self.t120 +
            self.t121 +
            self.t122 +
            self.t123 +
            self.t124 +
            self.t125 +
            self.t126 +
            self.t127 +
            self.t128 +
            self.t129 +
            self.t130 +
            self.t131 +
            self.t132 +
            self.t133 +
            self.t134 +
            self.t135 +
            self.t136 +
            self.t137 +
            self.t138 +
            self.t139 +
            self.t140 +
            self.t141 +
            self.t142 +
            self.t143 +
            self.t144 +
            self.t145
        )

        # This variable determines the total time spent in switch
        self.time_in_switch = self.switch1 * (Constants.t - self.switch_time)

        # This variable determines the tokens per string received
        self.income_in_switch = self.time_in_switch / Constants.secondsper_token

        # This is the sum of strings + production in switch
        self.total_production = self.production_strings + self.income_in_switch
