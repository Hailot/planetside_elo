from match import *
from captains import *
from update import *

lobby = []


def get_lobby():
    return lobby


def add_lobby(player):
    add(player, lobby)


def remove_lobby(player):
    remove(player, lobby)


def clear_lobby():
    clear(lobby)

