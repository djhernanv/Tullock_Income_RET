from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):
        yield (pages.CompetitionInstructions1)
        yield (pages.CompetitionInstructions2Example)
        yield (pages.CompetitionInstructions3)
        yield (pages.Beliefs, {'avgbelief': 10, 'mostprodBTbelief': 20})



