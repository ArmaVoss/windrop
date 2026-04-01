import sqlite3
from config import settings

def get_connection():
    conn = sqlite3.connect()