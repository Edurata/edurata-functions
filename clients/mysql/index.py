import mysql.connector
from mysql.connector import Error
import os
import json
from datetime import datetime
from decimal import Decimal
import uuid
import base64

# Function to convert complex objects to JSON-compatible format
def serialize_custom(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string
    elif isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')  # Encode binary data as base64 string
    elif isinstance(obj, uuid.UUID):
        return str(obj)  # Convert UUID object to string
    elif isinstance(obj, set):  
        return list(obj)  # Convert set to list
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

            # Convert complex data types before JSON serialization
            return {"result": result}

    except Error as e:
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Sample function call (commented out for reference)
# print(handler({"query": "INSERT INTO users2(id, username, email) VALUES (DEFAULT, 'test', 'example_email@example.com');"}, None)