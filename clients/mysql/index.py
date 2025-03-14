import mysql.connector
from mysql.connector import Error
import os
import json
from datetime import datetime

# Function to convert datetime objects to string
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')  # Format as needed
    raise TypeError(f"Type {type(obj)} not serializable")

# Main handler function
def handler(inputs):
    connection = None  
    cursor = None
    query = inputs.get('query')
    
    # Load database configuration from environment variables
    connection_config = {
        "host": os.getenv('MYSQL_HOST'),
        "user": os.getenv('MYSQL_USER'),
        "password": os.getenv('MYSQL_PASSWORD'),
        "database": os.getenv('MYSQL_DATABASE')
    }
    
    if not all(connection_config.values()):
        print(connection_config)
        return {"error": "Missing one or more required database environment variables."}

    try:
        connection = mysql.connector.connect(**connection_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            if query.strip().lower().startswith(("insert", "update", "delete")):
                connection.commit()
                return {"result": "Query executed successfully."}

            result = cursor.fetchall()

            # Convert datetime fields to strings before JSON serialization
            return {"result": json.dumps(result, default=serialize_datetime)}

    except Error as e:
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Sample function call (commented out for reference)
# print(handler({"query": "INSERT INTO users2(id, username, email) VALUES (DEFAULT, 'test', 'example_email@example.com');"}, None)