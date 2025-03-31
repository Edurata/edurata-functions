import os
import boto3
from typing import Any, Dict

dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

def handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
    operation = inputs['operation'].lower()
    table_name = inputs['table_name']
    table = dynamodb.Table(table_name)

    if operation == 'create':
        item = inputs.get('item')
        if not item:
            raise ValueError("Missing 'item' for create operation.")
        table.put_item(Item=item)
        return {"result": {"message": "Item created"}}

    elif operation == 'read':
        key = inputs.get('key')
        if not key:
            raise ValueError("Missing 'key' for read operation.")
        response = table.get_item(Key=key)
        return {"result": response.get("Item", {})}

    elif operation == 'update':
        key = inputs.get('key')
        item = inputs.get('item')
        if not key or not item:
            raise ValueError("Missing 'key' or 'item' for update operation.")
        update_expression = "SET " + ", ".join(f"#{k}=:{k}" for k in item)
        expression_attribute_names = {f"#{k}": k for k in item}
        expression_attribute_values = {f":{k}": v for k, v in item.items()}

        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        return {"result": {"message": "Item updated"}}

    elif operation == 'delete':
        key = inputs.get('key')
        if not key:
            raise ValueError("Missing 'key' for delete operation.")
        table.delete_item(Key=key)
        return {"result": {"message": "Item deleted"}}

    else:
        raise ValueError(f"Unsupported operation: {operation}")

# Sample test call
# print(handler({
#     "operation": "create",
#     "table_name": "MyTable",
#     "item": {"id": "123", "name": "Alice"}
# }))
