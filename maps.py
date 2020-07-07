from update import *

maps = [
    'Acan Southern',
    'Chac Fusion Labs',
    'Ghanan Southern',
    'Peris Eastern',
    'Xenotech Labs',
    'Pale Canyon'
]

map_match = [
    'Acan Southern',
    'Chac Fusion Labs',
    'Ghanan Southern',
    'Peris Eastern',
    'Xenotech Labs',
    'Pale Canyon'
]


def get_maps():
    return maps


def get_map_match():
    return map_match


def set_map_match(map):
    global map_match
    map_match = map


def add_map(map):
    add(map, maps)


def remove_map(map):
    remove(map, maps)


def remove_map_match(map):
    remove(map, map_match)


def reset_maps():
    global maps
    maps = [
        'Acan Southern',
        'Chac Fusion Labs',
        'Ghanan Southern',
        'Peris Eastern',
        'Xenotech Labs',
        'Pale Canyon'
    ]


def reset_map_match():
    global map_match
    map_match = [
        'Acan Southern',
        'Chac Fusion Labs',
        'Ghanan Southern',
        'Peris Eastern',
        'Xenotech Labs',
        'Pale Canyon'
    ]


def clear_maps():
    clear(maps)

