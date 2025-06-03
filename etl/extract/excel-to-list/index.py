import pandas as pd

def handler(inputs):
    file_path = inputs["file"]
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    # Convert dataframe rows to list of dicts (excluding header)
    records = df.to_dict(orient="records")

    return {"rows": records}

# Example usage
# outputs = handler({"file": "example.xlsx"})
# print(outputs)
