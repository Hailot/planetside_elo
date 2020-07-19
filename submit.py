import mariadb
from decouple import config
import sys
from update import *
import pyodbc

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user='root',
        password='pugs1337',
        host='db',
        database="planetside_data"
    )
    print('submit.py connected to MariaDB database')
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
myCursor = conn.cursor()


def submit(Match_ID):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                          'SERVER=test;'
                          f'DATABASE=[dbo].[elo_player_match_results] @i_vMatchId = {Match_ID};'
                          'UID=user;'
                          'PWD=password')
    pullCursor = cnxn.cursor()
    pullCursor.execute("select CharacterId from users where IsOnWinningTeam = 1")
    winningPlayers = pullCursor.fetchall()
    pullCursor.execute("select CharacterId from users where IsOnWinningTeam = 0")
    losingPlayers = pullCursor.fetchall()
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

