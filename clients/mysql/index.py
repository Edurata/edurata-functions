import mysql.connector
from mysql.connector import Error
import os
import json

# Main..
def handler(inputs, context):
    connection = None  
    cursor = None  # Ensure cursor is initialized
    query = inputs.get('query')
    
    # Load database configuration from environment variables
    connection_config = {
        "host": os.getenv('MYSQL_HOST'),
        "user": os.getenv('MYSQL_USER'),
        "password": os.getenv('MYSQL_PASSWORD'),
        "database": os.getenv('MYSQL_DATABASE')
    }
    
    # Ensure all required environment variables are set
    if not all(connection_config.values()):
        return {"error": "Missing one or more required database environment variables."}

    try:
        connection = mysql.connector.connect(**connection_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            # Check if the query is a modification query
            if query.strip().lower().startswith(("insert", "update", "delete")):
                connection.commit()
                return {"result": "Query executed successfully."}

            result = cursor.fetchall()
            return {"result": json.dumps(result)}

    except Error as e:
        return {"error": str(e)}

    finally:
        # Ensure both cursor and connection are closed
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Sample function call (commented out for reference)
# print(handler({"query": "INSERT INTO users2(id, username, email) VALUES (DEFAULT, 'test', 'example_email@example.com');"}, None)