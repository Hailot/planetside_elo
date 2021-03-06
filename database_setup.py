import mariadb
from decouple import config
import sys
from update import *

def setup_db():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user='root',
            password='pugs1337',
            host='db',
            database="planetside_data"
        )
        print('database_setup.py connected to MariaDB database')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    myCursor = conn.cursor()

    #Dropping players table if already exists.
    myCursor.execute("DROP TABLE IF EXISTS players")
    myCursor.execute("DROP TABLE IF EXISTS matches")
    myCursor.execute("DROP TABLE IF EXISTS match_players")
    myCursor.execute("DROP TABLE IF EXISTS planetside_users")


    #Creating table as per requirement
    players_sql ='''CREATE TABLE players(
    id INT AUTO_INCREMENT PRIMARY KEY,
    discord VARCHAR(255),
    wins INT,
    losses INT,
    is_teamcaptain TINYINT,
    is_active TINYINT,
    vs_char_id BIGINT,
    nc_char_id BIGINT,
    tr_char_id BIGINT
    )'''
    myCursor.execute(players_sql)

    matches_sql ='''CREATE TABLE matches(
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_a_captain_id INT,
    team_b_captain_id INT,
    team_a_score INT,
    team_b_score INT,
    is_active TINYINT,
    script_id VARCHAR(255),
    start_time BIGINT,
    end_time BIGINT
    )'''
    myCursor.execute(matches_sql)

    match_players_sql ='''CREATE TABLE match_players(
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT,
    character_id BIGINT,
    match_id INT
    )'''
    myCursor.execute(match_players_sql)
    
    planetside_users_sql ='''CREATE TABLE planetside_users(
    id INT AUTO_INCREMENT PRIMARY KEY,  
    discord VARCHAR(255),
    is_teamcaptain TINYINT
    )'''
    myCursor.execute(planetside_users_sql)

    #Add Foreign Keys
    myCursor.execute("ALTER TABLE matches ADD FOREIGN KEY (team_a_captain_id) REFERENCES players (id)")
    myCursor.execute("ALTER TABLE matches ADD FOREIGN KEY (team_b_captain_id) REFERENCES players (id)")
    myCursor.execute("ALTER TABLE match_players ADD FOREIGN KEY (match_id) REFERENCES matches (id)")
    myCursor.execute("ALTER TABLE match_players ADD FOREIGN KEY (player_id) REFERENCES players (id)")

    #Closing the connection
    conn.close()