from lobby import *
from match import *
from update import *

captains = []


def set_captain(player):
    add(player, captains)
    remove_match(player)


def remove_captain(player):
    remove(player, captains)


def clear_captains():
    clear(captains)

