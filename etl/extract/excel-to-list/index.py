import pandas as pd

def handler(inputs):
    file_path = inputs["file"]
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    # Print shape and info for debugging
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns.tolist()}")
    
    # Replace NaN with None so JSON will have null, not NaN
    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    
    # Print length of records for debugging
    print(f"Number of records: {len(records)}")
    
    # Ensure we're returning a flat list
    if isinstance(records, list):
        return {"rows": records}
    else:
        # If somehow we got a nested structure, flatten it
        flattened = []
        for record in records:
            if isinstance(record, list):
                flattened.extend(record)
            else:
                flattened.append(record)
        return {"rows": flattened}

# Example usage
# outputs = handler({"file": "Räderliste.xlsx"})
# print(outputs)
