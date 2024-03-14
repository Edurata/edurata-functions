import subprocess
import os

def handler(inputs):
    codePath = inputs['code']

    # Assuming codePath is a directory containing requirements.txt
    try:
        # Synchronously execute pip install in the codePath directory
        subprocess.check_call([os.sys.executable, '-m', 'pip', 'install', '-r', os.path.join(codePath, 'requirements.txt')])
        print('Python packages installed successfully.')
    except subprocess.CalledProcessError as error:
        print('Error installing Python packages:', error)
        return {'error': 'Failed to install Python packages'}

    return {'code': codePath}
