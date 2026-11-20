import sqlite3

def get_connection():
    conn = sqlite3.connect("vessel.db") 
    return conn