import mariadb
from decouple import config
import sys
from update import *

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user=config('LOCALHOST_USER'),
        password=config('LOCALHOST_PASSWORD'),
        host="192.0.2.1",
        port=3306,
        database="planetside_data"
    )
    print('submit.py connected to MariaDB database')
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
myCursor = conn.cursor()


def submit(Match_ID):
    allPlayers = []
    winningPlayers = []
    losingPlayers = []
    for player in allPlayers:
        if player:
            add(player, winningPlayers)
        else:
            add(player, losingPlayers)
    for winningPlayer in winningPlayers:
        myCursor.execute(
            f"SELECT `wins` FROM `players` WHERE `vs_char_id` = {winningPlayer} OR `nc_char_id` = {winningPlayer} OR `tr_char_id` = {winningPlayer}")
        winningPlayerWins = myCursor.fetchone()
        winningPlayerWins += 1
        try:
            myCursor.execute(
                f"Update `players` SET `wins` TO `{winningPlayerWins}` WHERE `vs_char_id` = {winningPlayer} OR `nc_char_id` = {winningPlayer} OR `tr_char_id` = {winningPlayer}")
        except mariadb.Error as er:
            print(f"Error: {er}")
        conn.commit()
    for losingPlayer in losingPlayers:
        myCursor.execute(
            f"SELECT `wins` FROM `players` WHERE `vs_char_id` = {losingPlayer} OR `nc_char_id` = {losingPlayer} OR `tr_char_id` = {losingPlayer}")
        losingPlayerLosses = myCursor.fetchone()
        losingPlayerLosses += 1
        try:
            myCursor.execute(
                f"Update `players` SET `wins` TO `{losingPlayerLosses}` WHERE `vs_char_id` = {losingPlayer} OR `nc_char_id` = {losingPlayer} OR `tr_char_id` = {losingPlayer}")
        except mariadb.Error as er:
            print(f"Error: {er}")
        conn.commit()

