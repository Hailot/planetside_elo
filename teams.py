from lobby import *


team_1 = []
team_2 = []
roster = [team_1, team_2]


def get_roster():
    return roster


def add_roster(player, team):
    add(player, roster[team])
    remove_match(player)


def clear_roster():
    clear(team_1)
    clear(team_2)
    clear_match()

