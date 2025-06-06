import pandas as pd

def handler(inputs):
    file_path = inputs["file"]
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    # Replace NaN with None so JSON will have null, not NaN
    records = df.where(pd.notnull(df), None).to_dict(orient="records")

    return {"rows": records}

# Example usage
# outputs = handler({"file": "Räderliste.xlsx"})
# print(outputs)
