import os
import mysql.connector

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

# Establish a connection
try:
    conn = mysql.connector.connect(**DB_CONFIG)
except mysql.connector.Error as e:
    print("Error connecting to the database:", e)
