import os
import json
import yaml

def handler(inputs):
    input_path = inputs["input_file"]
    output_format = inputs["output_format"].lower()

    if output_format not in ["json", "yaml"]:
        raise ValueError("Invalid output format. Must be 'json' or 'yaml'.")

    with open(input_path, "r") as infile:
        if input_path.endswith(".yaml") or input_path.endswith(".yml"):
            data = yaml.safe_load(infile)
        elif input_path.endswith(".json"):
            data = json.load(infile)
        else:
            raise ValueError("Input file must be .json or .yaml/.yml")

    # Determine output path
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_ext = "json" if output_format == "json" else "yaml"
    output_path = f"/tmp/{base_name}_converted.{output_ext}"

    with open(output_path, "w") as outfile:
        if output_format == "json":
            json.dump(data, outfile, indent=2)
        else:
            yaml.safe_dump(data, outfile, sort_keys=False)

    return {"output_file": output_path}

# Example usage:
# handler({
#     "input_file": "example.yaml",
#     "output_format": "json"
# })
