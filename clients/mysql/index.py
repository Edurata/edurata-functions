import mysql.connector
from mysql.connector import Error
import os
import json

# Main..
def handler(inputs, context):
    connection = None  # Initialize connection variable
    query = inputs['query']
    connection_config = {
        "host": os.getenv('MYSQL_HOST'),
        "user": os.getenv('MYSQL_USER'),
        "password": os.getenv('MYSQL_PASSWORD'),
        "database": os.getenv('MYSQL_DATABASE')
    }
    try:
        connection = mysql.connector.connect(**connection_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchall()
            return {"result": json.dumps(result)}
    except Error as e:
        return {"error": str(e)}
    finally:
        if connection and connection.is_connected():  # Check if connection is not None
            cursor.close()
            connection.close()

# Sample function call (commented out for reference)
# print(handler({"query": "INSERT INTO users2(id, username, email) VALUES (DEFAULT, 'test', 'example_email@example.com');"}, None))
