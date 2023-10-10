import pandas as pd

class PandasWrapper:
    def __init__(self, data):
        self.data = data

    def head(self, n=5):
        return self.data.head(n)

    def tail(self, n=5):
        return self.data.tail(n)

    def describe(self):
        return self.data.describe()

    # Add more methods for other pandas functions as needed

def handler(input_data):
    try:
        data = pd.DataFrame(input_data['data'])
        function_name = input_data['function_name']
        params = input_data.get('params', {})
        
        wrapper = PandasWrapper(data)

        if hasattr(wrapper, function_name):
            func = getattr(wrapper, function_name)
            result = func(**params)
            return result.to_dict(orient='records')
        else:
            return f"Function '{function_name}' not found."

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    import json
    import sys

    input_data = json.load(sys.stdin)
    result = handler(input_data)
    print(json.dumps(result))
