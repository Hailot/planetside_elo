from lobby import *

factions = ['VS', 'NC', 'TR']
factions_team = []


def get_faction():
    return factions


def get_faction_team():
    return factions


def set_faction_team(faction, team):
    factions_team.insert(faction, team)
    remove(faction, factions)


def clear_faction_teams():
    global factions
    factions = ['VS', 'NC', 'TR']
    clear(factions_team)

