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
            port=3306,
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
    myCursor.execute("DROP TABLE IF EXISTS planetside_users")


    #Creating table as per requirement
    players_sql ='''CREATE TABLE players(
    id INT AUTO_INCREMENT PRIMARY KEY,  
    vs_char_id INT,
    nc_char_id INT,
    tr_char_id INT,
    wins INT
    )'''
    myCursor.execute(players_sql)
    
    planetside_users_sql ='''CREATE TABLE planetside_users(
    id INT AUTO_INCREMENT PRIMARY KEY,  
    discord VARCHAR(255),
    is_teamcaptain TINYINT
    )'''
    myCursor.execute(planetside_users_sql)

    #Closing the connection
    conn.close()