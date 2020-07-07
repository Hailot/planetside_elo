from lobby import *
from update import *

players = []


def set_match():
    global players
    players = get_lobby()
    clear_lobby()


def get_match():
    return players


def add_match(player):
    add(player, players)


def remove_match(player):
    remove(player, players)


def clear_match():
    clear(players)

