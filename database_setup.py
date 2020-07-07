import mariadb
from decouple import config
import sys
from update import *

def setup_db():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=config('DATABASE_USER'),
            password=config('DATABASE_PASSWORD'),
            host=config('DATABASE_HOST'),
            port=config('DATABASE_PORT'),
            database="planetside_data"
        )
        print('submit.py connected to MariaDB database')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    myCursor = conn.cursor()

    #Dropping players table if already exists.
    cursor.execute("DROP TABLE IF EXISTS players")
    cursor.execute("DROP TABLE IF EXISTS players")


    #Creating table as per requirement
    sql ='''CREATE TABLE players(
    vs_char_id INT,
    nc_char_id INT,
    tr_char_id INT,
    wins INT
    )'''
    cursor.execute(sql)

    #Closing the connection
    conn.close()