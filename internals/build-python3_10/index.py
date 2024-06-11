import subprocess
import os
import re

# This is necessary in case python is run in a lambda
def modify_handler_signature(code):
    # Define the regular expression pattern
    pattern = r"def handler\(([^,)]+)\):"
    
    # Define the replacement string
    replacement = r"def handler(\1, additional_parameter = 'Dummy'):"
    
    # Perform the substitution
    modified_code = re.sub(pattern, replacement, code)
    
    return modified_code

def modify_handlers_recursively(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r+') as file:
                    content = file.read()
                    modified_content = modify_handler_signature(content)
                    file.seek(0)
                    file.write(modified_content)
                    file.truncate()

def handler(inputs):
    codePath = inputs['code']
    python_modules_path = codePath

    # Modify handler signature recursively
    modify_handlers_recursively(codePath)

    # Assuming codePath is a directory containing requirements.txt
    try:
        # Synchronously execute pip install in the codePath directory
        # Install directly in root directory
        subprocess.check_call([os.sys.executable, '-m', 'pip', 'install', '-r', os.path.join(codePath, 'requirements.txt'), '-t', python_modules_path])

        print('Python packages installed successfully in', python_modules_path)

        # List all files and folders on the first level of codePath directory
        files_and_folders = os.listdir(codePath)
        print('Files and folders in', codePath, ':', files_and_folders)

    except subprocess.CalledProcessError as error:
        print('Error installing Python packages:', error)
        return {'code': codePath}

    return {'code': codePath}
